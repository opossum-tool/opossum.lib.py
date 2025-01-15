<!--
SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>

SPDX-License-Identifier: Apache-2.0
-->

# opossum.lib.py

[![REUSE status](https://api.reuse.software/badge/git.fsfe.org/reuse/api)](https://api.reuse.software/info/git.fsfe.org/reuse/api)
![Lint and test](https://github.com/opossum-tool/opossum.lib.py/actions/workflows/lint_and_run_tests.yml/badge.svg)
![build workflow](https://github.com/opossum-tool/opossum.lib.py/actions/workflows/build-and-e2e-test.yml/badge.svg)

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
The CLI uses subcommands. The main command just displays all available subcommands
```bash
Usage: uv run opossum-file [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  generate  Generate an Opossum file from various other file formats.
```

### `generate`

```bash
Usage: uv run opossum-file generate [OPTIONS]

  Generate an Opossum file from various other file formats.

  Currently supported input formats:
    - SPDX

Options:
  --spdx PATH         SPDX files used as input.
  -o, --outfile TEXT  The file path to write the generated opossum document
                      to. If appropriate, the extension ".opossum" will be
                      appended.  [default: output.opossum]
  --help              Show this message and exit.

```

# Development

To test your changes, run

```bash
uv run ruff check
uv run ruff format --check
uv run python -m mypy src/ tests/
uv run pytest
```

# Build

To build, run

```bash
uv run python build.py opossum-file
```

This will create a self-contained executable file `dist/opossum-file` (`dist/opossum-file.exe` on Windows).
