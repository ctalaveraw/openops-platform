#!/bin/sh
# Temporary fixture for proving the repository shell gate in CI.
# Remove this file after the hosted failure and recovery checks.
message="hello world"
printf '%s\n' $message
