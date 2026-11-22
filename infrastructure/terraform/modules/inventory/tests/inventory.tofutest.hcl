variables {
  host_name    = "fixture-node"
  architecture = "arm64"
}

run "arm64_inventory" {
  command = plan

  assert {
    condition     = output.inventory.schema_version == 1
    error_message = "Unexpected inventory version."
  }

  assert {
    condition     = length(output.inventory.hosts) == 1 && output.inventory.hosts["fixture-node"].architecture == "arm64"
    error_message = "Expected one ARM64 fixture host."
  }
}

run "amd64_inventory" {
  command = plan

  variables {
    host_name    = "fixture-x86"
    architecture = "amd64"
  }

  assert {
    condition     = length(output.inventory.hosts) == 1 && output.inventory.hosts["fixture-x86"].architecture == "amd64"
    error_message = "Expected one AMD64 fixture host."
  }
}

run "invalid_host_name" {
  command = plan

  variables {
    host_name = "bad host"
  }

  expect_failures = [var.host_name]
}

run "invalid_architecture" {
  command = plan

  variables {
    architecture = "unknown"
  }

  expect_failures = [var.architecture]
}
