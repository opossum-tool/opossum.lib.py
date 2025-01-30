#  SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#  #
#  SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from opossum_lib.shared.entities.opossum_input_file_model import FrequentLicenseModel


class FrequentLicense(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    full_name: str
    short_name: str
    default_text: str

    def to_opossum_model(self) -> FrequentLicenseModel:
        return FrequentLicenseModel(
            full_name=self.full_name,
            short_name=self.short_name,
            default_text=self.default_text,
        )
