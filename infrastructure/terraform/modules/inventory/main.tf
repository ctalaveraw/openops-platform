terraform {
  required_version = "= 1.13.9"
}

variable "host_name" {
  type     = string
  nullable = false

  validation {
    condition     = can(regex("^[a-z]([a-z0-9-]{0,61}[a-z0-9])?$", var.host_name))
    error_message = "Use a lowercase host label of 1 to 63 characters."
  }
}

variable "architecture" {
  type     = string
  nullable = false

  validation {
    condition     = contains(["amd64", "arm64"], var.architecture)
    error_message = "Architecture must be amd64 or arm64."
  }
}

output "inventory" {
  description = "Candidate host metadata for configuration management."
  value = {
    schema_version = 1
    hosts = {
      (var.host_name) = {
        architecture = var.architecture
      }
    }
  }
}
