# Infrastructure checks

Run these commands from the infrastructure directory.

| Command | Expected result |
| --- | --- |
| `make init` | Local initialization without a remote backend |
| `make lint` | HCL already formatted |
| `make validate` | Valid module configuration |
| `make test` | Four native test runs pass |
| `make prose-check` | All three Markdown files score 5/5 |
| `make check` | All required checks pass |

The test file uses plan mode in each run. It checks the output for ARM64 and
AMD64 and expects invalid host names and architectures to fail validation.
No apply or external provider is used. Tests do not create stateful resources.

If the CLI is missing or the version differs, install the pinned release.
If validation reports missing initialization, run the init target separately.
For a formatting failure, inspect the diff and run the following command:

```sh
tofu fmt -recursive terraform
```

To verify failure propagation, change the invalid host test's
`host_name` to a valid label and rerun the test. Restore the test afterward.
The suite must report a failure because the expected rejection did not occur.

Do not commit generated state or plans. There is no root CI delegation or cloud
acceptance test yet.
