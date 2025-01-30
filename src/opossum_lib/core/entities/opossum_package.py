#  SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#  #
#  SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from opossum_lib.core.entities.source_info import SourceInfo
from opossum_lib.shared.entities.opossum_input_file_model import OpossumPackageModel


class OpossumPackage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    source: SourceInfo
    attribution_confidence: int | None = None
    comment: str | None = None
    package_name: str | None = None
    package_version: str | None = None
    package_namespace: str | None = None
    package_type: str | None = None
    package_purl_appendix: str | None = None
    copyright: str | None = None
    license_name: str | None = None
    license_text: str | None = None
    url: str | None = None
    first_party: bool | None = None
    exclude_from_notice: bool | None = None
    pre_selected: bool | None = None
    follow_up: Literal["FOLLOW_UP"] | None = None
    origin_id: str | None = None
    origin_ids: tuple[str, ...] | None = None
    criticality: Literal["high"] | Literal["medium"] | None = None
    was_preferred: bool | None = None

    def to_opossum_model(self) -> OpossumPackageModel:
        return OpossumPackageModel(
            source=self.source.to_opossum_model(),
            attribution_confidence=self.attribution_confidence,
            comment=self.comment,
            package_name=self.package_name,
            package_version=self.package_version,
            package_namespace=self.package_namespace,
            package_type=self.package_type,
            package_p_u_r_l_appendix=self.package_purl_appendix,
            copyright=self.copyright,
            license_name=self.license_name,
            license_text=self.license_text,
            url=self.url,
            first_party=self.first_party,
            exclude_from_notice=self.exclude_from_notice,
            pre_selected=self.pre_selected,
            follow_up=self.follow_up,
            origin_id=self.origin_id,
            origin_ids=self.origin_ids,
            criticality=self.criticality,
            was_preferred=self.was_preferred,
        )
