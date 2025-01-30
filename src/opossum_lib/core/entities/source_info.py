#  SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#  #
#  SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from opossum_lib.shared.entities.opossum_input_file_model import SourceInfoModel


class SourceInfo(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str
    document_confidence: int | float | None = 0
    additional_name: str | None = None

    def to_opossum_model(self) -> SourceInfoModel:
        return SourceInfoModel(
            name=self.name,
            document_confidence=self.document_confidence,
            additional_name=self.additional_name,
        )
