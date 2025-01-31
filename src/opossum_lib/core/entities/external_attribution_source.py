#  SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#  #
#  SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from opossum_lib.shared.entities.opossum_input_file_model import (
    ExternalAttributionSourceModel,
)


class ExternalAttributionSource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str
    priority: int
    is_relevant_for_preferred: bool | None = None

    def to_opossum_file_model(self) -> ExternalAttributionSourceModel:
        return ExternalAttributionSourceModel(
            name=self.name,
            priority=self.priority,
            is_relevant_for_preferred=self.is_relevant_for_preferred,
        )
