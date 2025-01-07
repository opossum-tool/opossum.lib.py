<!--
SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>

SPDX-License-Identifier: Apache-2.0
-->

# opossum.lib.py

[![REUSE status](https://api.reuse.software/badge/git.fsfe.org/reuse/api)](https://api.reuse.software/info/git.fsfe.org/reuse/api)
![Lint and test](https://github.com/opossum-tool/opossum.lib.py/actions/workflows/lint_and_run_tests.yml/badge.svg)

This is a library to convert an SPDX document to a file readable by [OpossumUI](https://github.com/opossum-tool/OpossumUI/).

# Current state

This is a work in progress and not yet stable.

# License

[Apache-2.0](LICENSE)

# Installation

This package uses [uv](https://docs.astral.sh/uv/) for installation and dependency management.
After installing uv, you can set up the project with

```bash
uv sync
```

# How to use

## Command-line usage

```bash
Usage: uv run spdx2opossum [OPTIONS]

  CLI-tool for converting SPDX documents to Opossum documents.

Options:
  -i, --infile PATH   The file containing the document to be converted.
                      [required]
  -o, --outfile TEXT  The file path to write the generated opossum document
                      to. The generated file will be an opossum file, if the
                      specified file path doesn't match this file extension
                      ".opossum" will be appended.
  --help              Show this message and exit.

```

# Development

To test your changes, run

```bash
uv run pytest
uv run python -m mypy src/ tests/
```

The package uses pre-commit hooks to check the code style of your changes.
It also provides a script `(./scripts/linter_and_formatting.sh)` to make your changes compliant with the expected
code style. To use this script under linux run

```bash
./scripts/linter_and_formatting.sh  # in the root of the repo
```
