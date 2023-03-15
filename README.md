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

As always you should work in a virtualenv (venv). This package uses [poetry](https://python-poetry.org/) for installation
and dependency management. To install the local clone of this repo run
```
poetry install  # in the root of the repo
```

# How to use

## Command-line usage
```
Usage: spdx2opossum [OPTIONS]

  CLI-tool for converting SPDX documents to Opossum documents.

Options:
  -i, --infile PATH   The file containing the document to be converted.
                      [required]
  -o, --outfile TEXT  The file path to write the generated opossum document
                      to. The generated file will be in JSON format, if the
                      specified file path doesn't match this file extension
                      ".json" will be appended.
  --help              Show this message and exit.

```
# Development

To test your changes run 

```
poetry run pytest  # in the root of the repo
```

The package provides a script `(./scripts/linter_and_formatting.sh)` to make your changes compliant with the expected 
code style. To use this script under linux run
```
chmod +x ./scripts/linter_and_formatting.sh  # in the root of the repo
./scripts/linter_and_formatting.sh  # in the root of the repo
```