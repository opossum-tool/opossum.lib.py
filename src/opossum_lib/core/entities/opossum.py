# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from opossum_lib.core.entities.scan_results import ScanResults
from opossum_lib.shared.entities.opossum_file_model import OpossumFileModel
from opossum_lib.shared.entities.opossum_output_file_model import OpossumOutputFileModel

type OpossumPackageIdentifier = str
type ResourcePath = str


class Opossum(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    scan_results: ScanResults
    review_results: OpossumOutputFileModel | None = None

    def to_opossum_file_model(self) -> OpossumFileModel:
        return OpossumFileModel(
            input_file=self.scan_results.to_opossum_file_model(),
            output_file=self.review_results,
        )
