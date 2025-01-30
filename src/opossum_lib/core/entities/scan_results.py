#  SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#  #
#  SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import uuid
from collections import defaultdict
from copy import deepcopy
from dataclasses import field

from pydantic import BaseModel, ConfigDict

from opossum_lib.core.entities.base_url_for_sources import BaseUrlsForSources
from opossum_lib.core.entities.external_attribution_source import (
    ExternalAttributionSource,
)
from opossum_lib.core.entities.frequent_license import FrequentLicense
from opossum_lib.core.entities.metadata import Metadata
from opossum_lib.core.entities.opossum_package import OpossumPackage
from opossum_lib.core.entities.resource import Resource, _convert_path_to_str
from opossum_lib.shared.entities.opossum_input_file_model import (
    OpossumInputFileModel,
    OpossumPackageIdentifierModel,
    OpossumPackageModel,
    ResourcePathModel,
)


def _default_attribution_id_mapper() -> dict[OpossumPackage, str]:
    return defaultdict(lambda: str(uuid.uuid4()))


class ScanResults(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    metadata: Metadata
    resources: list[Resource]
    attribution_breakpoints: list[str] = []
    external_attribution_sources: dict[str, ExternalAttributionSource] = {}
    frequent_licenses: list[FrequentLicense] | None = None
    files_with_children: list[str] | None = None
    base_urls_for_sources: BaseUrlsForSources | None = None
    attribution_to_id: dict[OpossumPackage, str] = field(
        default_factory=_default_attribution_id_mapper
    )
    unassigned_attributions: list[OpossumPackage] = []

    def to_opossum_model(self) -> OpossumInputFileModel:
        external_attributions, resources_to_attributions = (
            self.create_attribution_mapping(self.resources)
        )
        external_attributions.update(self._get_unassigned_attributions())

        frequent_licenses = None
        if self.frequent_licenses:
            frequent_licenses = [
                license.to_opossum_model() for license in self.frequent_licenses
            ]
        base_urls_for_sources = (
            self.base_urls_for_sources and self.base_urls_for_sources.to_opossum_model()
        )

        external_attribution_sources = {
            key: val.to_opossum_model()
            for (key, val) in self.external_attribution_sources.items()
        }

        return OpossumInputFileModel(
            metadata=self.metadata.to_opossum_model(),
            resources={
                str(resource.path): resource.to_opossum_model()
                for resource in self.resources
            },
            external_attributions=external_attributions,
            resources_to_attributions=resources_to_attributions,
            attribution_breakpoints=deepcopy(self.attribution_breakpoints),
            external_attribution_sources=external_attribution_sources,
            frequent_licenses=frequent_licenses,
            files_with_children=deepcopy(self.files_with_children),
            base_urls_for_sources=base_urls_for_sources,
        )

    def _get_unassigned_attributions(
        self,
    ) -> dict[OpossumPackageIdentifierModel, OpossumPackageModel]:
        if self.unassigned_attributions:
            result = {}
            for unassigned_attribution in self.unassigned_attributions:
                if unassigned_attribution in self.attribution_to_id:
                    package_identifier = self.attribution_to_id[unassigned_attribution]
                    result[package_identifier] = (
                        unassigned_attribution.to_opossum_model()
                    )
                else:
                    package_identifier = str(uuid.uuid4())
                    self.attribution_to_id[unassigned_attribution] = package_identifier
                    result[package_identifier] = (
                        unassigned_attribution.to_opossum_model()
                    )
            return result
        else:
            return {}

    def create_attribution_mapping(
        self,
        root_nodes: list[Resource],
    ) -> tuple[
        dict[OpossumPackageIdentifierModel, OpossumPackageModel],
        dict[ResourcePathModel, list[OpossumPackageIdentifierModel]],
    ]:
        external_attributions: dict[
            OpossumPackageIdentifierModel, OpossumPackageModel
        ] = {}
        resources_to_attributions: dict[
            ResourcePathModel, list[OpossumPackageIdentifierModel]
        ] = {}

        def process_node(node: Resource) -> None:
            path = _convert_path_to_str(node.path)
            if not path.startswith("/"):
                # the / is required by OpossumUI
                path = "/" + path

            node_attributions_by_id = {
                self.get_attribution_key(a): a.to_opossum_model()
                for a in node.attributions
            }
            external_attributions.update(node_attributions_by_id)

            if len(node_attributions_by_id) > 0:
                resources_to_attributions[path] = list(node_attributions_by_id.keys())

            for child in node.children.values():
                process_node(child)

        for root in root_nodes:
            process_node(root)

        return external_attributions, resources_to_attributions

    def get_attribution_key(
        self, attribution: OpossumPackage
    ) -> OpossumPackageIdentifierModel:
        id = self.attribution_to_id[attribution]
        self.attribution_to_id[attribution] = id
        return id
