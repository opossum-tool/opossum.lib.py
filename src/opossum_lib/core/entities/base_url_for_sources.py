#  SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#  #
#  SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from opossum_lib.shared.entities.opossum_input_file_model import BaseUrlsForSourcesModel


class BaseUrlsForSources(BaseModel):
    model_config = ConfigDict(frozen=True, extra="allow")

    def to_opossum_model(self) -> BaseUrlsForSourcesModel:
        return BaseUrlsForSourcesModel(**self.model_dump())
