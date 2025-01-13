# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import os.path

from pydantic import BaseModel
from pydantic_core import SchemaValidator


def path_segments(path: str) -> list[str]:
    path = os.path.normpath(path)
    return path.split(os.sep)


def check_schema(model: BaseModel) -> None:
    schema_validator = SchemaValidator(schema=model.__pydantic_core_schema__)
    schema_validator.validate_python(model.__dict__)
