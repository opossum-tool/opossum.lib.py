#  SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#  #
#  SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from opossum_lib.shared.entities.opossum_input_file_model import MetadataModel


class Metadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="allow")
    project_id: str
    file_creation_date: str
    project_title: str
    project_version: str | None = None
    expected_release_date: str | None = None
    build_date: str | None = None

    def to_opossum_file_model(self) -> MetadataModel:
        return MetadataModel(**self.model_dump())
