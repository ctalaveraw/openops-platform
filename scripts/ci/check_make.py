#!/usr/bin/env python3
"""Check Makefile source and the literal help/check interface without execution."""

import os  # Decode Git filenames safely.
import re  # Find the public check command in the help recipe's source.
import subprocess  # Discover files through Git, without invoking Make.
import sys  # Pass the wrapper's exit status back to Make.
from pathlib import Path  # Locate this checkout independently of the caller.

ROOT = Path(__file__).resolve().parents[2]
STANDALONE = {"Makefile", "makefile", "GNUmakefile"}
FRAGMENTS = {".mk", ".make"}
REQUIRED = {"help", "check"}


def make_inputs() -> list[Path]:
    # Select tracked files and new nonignored files, using NUL-safe filenames.
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    )
    paths = {ROOT / os.fsdecode(name) for name in listed.stdout.split(b"\0") if name}
    return sorted(
        path
        for path in paths
        if (path.name in STANDALONE or path.suffix in FRAGMENTS)
        and not path.is_relative_to(ROOT / "vendor")
        and path.is_file()
    )


def make_findings(path: Path, parser) -> list[str]:
    # Decode explicitly: malformed UTF-8 is a content finding.
    # Normalizing line endings here leaves the source file unchanged.
    source = path.read_text(encoding="utf-8")
    tree = parser.parse(source.encode("utf-8"))

    # Walk the syntax tree, including tokens that the parser had to invent.
    pending = [tree.root_node]
    while pending:
        node = pending.pop()
        line = node.start_point.row + 1
        if node.is_error or node.is_missing:
            return [f"{line}: invalid Makefile syntax ({node.type})"]
        if node.type in {"targets", "prerequisites"}:
            # This grammar can merge an unindented recipe into the next header.
            # A header may span lines only through an explicit continuation.
            header = node.text.decode().replace("\\\n", "")
            if "\n" in header:
                return [f"{line}: header crosses a newline; check recipe TABs"]
        if node.type == "RECIPEPREFIX_assignment":
            return [f"{line}: custom .RECIPEPREFIX needs a parser review"]
        pending.extend(reversed(node.children))

    # Fragments receive syntax checks. Standalone files expose an interface.
    if path.name not in STANDALONE:
        return []

    rules = {}
    phony = set()
    for node in tree.root_node.named_children:
        # Only unconditional, literal declarations establish the interface.
        if node.type != "rule":
            continue
        targets = next(child for child in node.children if child.type == "targets")
        names = {
            child.text.decode() for child in targets.children if child.type == "word"
        }
        for name in names:
            rules[name] = node
        if ".PHONY" in names:
            prerequisites = node.child_by_field_name("normal")
            if prerequisites is not None:
                phony.update(
                    child.text.decode()
                    for child in prerequisites.children
                    if child.type == "word"
                )

    findings = []
    for name in sorted(REQUIRED):
        if name not in rules:
            findings.append(f"1: declare an unconditional literal {name}: target")
        if name not in phony:
            findings.append(f"1: declare {name} in .PHONY")

    # Check documentation as source, without running the help recipe.
    if "help" in rules:
        recipe = next(
            (child for child in rules["help"].children if child.type == "recipe"), None
        )
        if recipe is None or not re.search(
            r"(?<![\w-])check(?![\w-])", recipe.text.decode()
        ):
            findings.append("1: the help recipe must mention the check command")
    return findings


def main() -> int:
    # Match the other required wrappers: callers cannot narrow the file scope.
    if len(sys.argv) != 1:
        print(
            "ERROR lint-make: this command accepts no path arguments.", file=sys.stderr
        )
        return 2

    try:
        # The engine builds a syntax tree; the language package supplies grammar.
        import tree_sitter_make
        from tree_sitter import Language, Parser

        parser = Parser(Language(tree_sitter_make.language()))
        paths = make_inputs()
        if ROOT / "Makefile" not in paths:
            raise ValueError("the root Makefile must be present")

        print(f"RUN lint-make: {len(paths)} file(s)", flush=True)
        failures = 0
        for path in paths:
            try:
                findings = make_findings(path, parser)
            except UnicodeDecodeError as error:
                findings = [f"1: invalid UTF-8: {error}"]
            for finding in findings:
                print(
                    f"FAIL lint-make: {path.relative_to(ROOT)}:{finding}",
                    file=sys.stderr,
                )
            failures += bool(findings)

    except (ImportError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(
            f"ERROR lint-make: {error}. Run make setup if tooling is missing.",
            file=sys.stderr,
        )
        return 2

    if failures:
        print(f"FAIL lint-make: {failures} file(s) failed.", file=sys.stderr)
        return 1

    print("PASS lint-make", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
