# Engineering writing standard

Use this standard for README files, ADRs, runbooks, issue descriptions,
pull requests, review comments, commit messages and external project updates.

## Write for maintainers

State the changed behavior and the reason for it. Name the affected files or
components. Give the command used to verify a claim and its observed result.
Separate completed work from proposals and untested behavior. Prefer short
sentences, direct verbs and familiar technical terms.

For an issue, describe a reproducible problem and what completion would prove.
For a pull request, explain the change, relevant checks, limitations and
follow-up work. For a commit, name the technical change without narrating the
development process. Write review comments against specific code or evidence.

Never include private conversation names, numbered workstream labels, chat
part numbers or assistant coordination terminology in repository records.

## Remove filler

Avoid promotional claims, unsupported certainty, vague attribution and generic
closing summaries. Remove stock AI phrases, forced contrasts, repetitive
three-part rhetoric and ornamental formatting. Prefer an observable statement:

> The JSON check exits nonzero when a fixture contains malformed input.

Do not claim a test passed unless it ran. Link measurements and decisions to
the command output, CI run, issue or source that supports them.

## Review before publishing

Run the repository's vendored SlopMonster checker on changed documentation:

```sh
make lint-prose
```

For text outside the lint target, such as a draft PR description, save the
text to a temporary Markdown file and run:

```sh
python3 vendor/slopmonster/deslop.py /tmp/openops-review.md
```

Correct findings without changing the checker's rules. SlopMonster is a
pattern checker, not an authorship test. A clean score does not establish
accuracy or useful documentation. Review the final text manually.

## Editing references

- [Google developer documentation style guide](https://developers.google.com/style/)
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
