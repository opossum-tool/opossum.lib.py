# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import uuid
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import field
from enum import Enum, auto
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

import opossum_lib.opossum.opossum_file as opossum_file
import opossum_lib.opossum.opossum_file_content as opossum_file_content
from opossum_lib.opossum.output_model import OpossumOutputFile

type OpossumPackageIdentifier = str
type ResourcePath = str


def default_attribution_id_mapper() -> dict[OpossumPackage, str]:
    return defaultdict(lambda: str(uuid.uuid4()))


class Opossum(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    metadata: Metadata
    resources: list[Resource]
    attribution_breakpoints: list[str] = field(default_factory=list)
    external_attribution_sources: dict[str, ExternalAttributionSource] = field(
        default_factory=dict
    )
    frequent_licenses: list[FrequentLicense] | None = None
    files_with_children: list[str] | None = None
    base_urls_for_sources: BaseUrlsForSources | None = None
    attribution_to_id: dict[OpossumPackage, str] = field(
        default_factory=default_attribution_id_mapper
    )
    output_file: OpossumOutputFile | None = None

    def to_opossum_file_format(self) -> opossum_file_content.OpossumFileContent:
        external_attributions, resources_to_attributions = (
            self.create_attribution_mapping(self.resources)
        )
        frequent_licenses = (
            None
            if self.frequent_licenses is None
            else [
                license.to_opossum_file_format() for license in self.frequent_licenses
            ]
        )
        base_urls_for_sources = (
            self.base_urls_for_sources
            and self.base_urls_for_sources.to_opossum_file_format()
        )
        return opossum_file_content.OpossumFileContent(
            input_file=opossum_file.OpossumInformation(
                metadata=self.metadata.to_opossum_file_format(),
                resources={
                    str(resource.path): resource.to_opossum_file_format()
                    for resource in self.resources
                },
                external_attributions=external_attributions,
                resources_to_attributions=resources_to_attributions,
                attribution_breakpoints=self.attribution_breakpoints,
                external_attribution_sources=self.external_attribution_sources,
                frequent_licenses=frequent_licenses,
                files_with_children=self.files_with_children,
                base_urls_for_sources=base_urls_for_sources,
            ),
            output_file=self.output_file,
        )

    def create_attribution_mapping(
        self,
        root_nodes: list[Resource],
    ) -> tuple[
        dict[opossum_file.OpossumPackageIdentifier, opossum_file.OpossumPackage],
        dict[opossum_file.ResourcePath, list[opossum_file.OpossumPackageIdentifier]],
    ]:
        external_attributions: dict[
            opossum_file.OpossumPackageIdentifier, opossum_file.OpossumPackage
        ] = {}
        resources_to_attributions: dict[
            opossum_file.ResourcePath, list[opossum_file.OpossumPackageIdentifier]
        ] = {}

        def process_node(node: Resource) -> None:
            path = str(node.path)
            if not path.startswith("/"):
                # the / is required by OpossumUI
                path = "/" + path
            attributions = node.attributions

            new_attributions_with_id = {
                self.get_attribution_key(a): a.to_opossum_file_format()
                for a in attributions
            }
            external_attributions.update(new_attributions_with_id)

            if len(new_attributions_with_id) > 0:
                resources_to_attributions[path] = list(new_attributions_with_id.keys())

            for child in node.children.values():
                process_node(child)

        for root in root_nodes:
            process_node(root)

        return external_attributions, resources_to_attributions

    def get_attribution_key(
        self, attribution: OpossumPackage
    ) -> OpossumPackageIdentifier:
        id = self.attribution_to_id[attribution]
        self.attribution_to_id[attribution] = id
        return id


class Resource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: Path
    type: ResourceType | None = None
    attributions: list[OpossumPackage] = []
    children: dict[str, Resource] = {}

    def to_opossum_file_format(self) -> opossum_file.ResourceInFile:
        if self.type == ResourceType.FILE:
            return 1
        else:
            return {
                str(child.path.relative_to(self.path)): child.to_opossum_file_format()
                for child in self.children.values()
            }

    def add_resource(self, resource: Resource) -> None:
        if not resource.path.is_relative_to(self.path):
            raise RuntimeError(
                f"The path {resource.path} is not a child of this node at {self.path}."
            )
        remaining_path_parts = resource.path.relative_to(self.path).parts
        if remaining_path_parts:
            self._add_resource(resource, remaining_path_parts)
        else:
            self._update(resource)

    def _add_resource(
        self, resource: Resource, remaining_path_parts: Iterable[str]
    ) -> None:
        if not remaining_path_parts:
            self._update(resource)
            return
        next, *rest_parts = remaining_path_parts
        if next not in self.children:
            self.children[next] = Resource(path=self.path / next)
        self.children[next]._add_resource(resource, rest_parts)

    def _update(self, other: Resource) -> None:
        if self.path != other.path:
            raise RuntimeError(
                "Trying to merge nodes with different paths: "
                + f"{self.path} vs. {other.path}"
            )
        if self.type and other.type and self.type != other.type:
            raise RuntimeError("Trying to merge incompatible node types.")
        self.type = self.type or other.type
        self.attributions.extend(other.attributions)
        for key, child in other.children.items():
            if key in self.children:
                self.children[key]._update(child)
            else:
                self.children[key] = child


class BaseUrlsForSources(BaseModel):
    model_config = ConfigDict(frozen=True, extra="allow")

    def to_opossum_file_format(self) -> opossum_file.BaseUrlsForSources:
        return opossum_file.BaseUrlsForSources(**self.model_dump())


class FrequentLicense(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    full_name: str
    short_name: str
    default_text: str

    def to_opossum_file_format(self) -> opossum_file.FrequentLicense:
        return opossum_file.FrequentLicense(**self.model_dump())


class SourceInfo(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str
    document_confidence: int | float | None = 0
    additional_name: str | None = None

    def to_opossum_file_format(self) -> opossum_file.SourceInfo:
        return opossum_file.SourceInfo(**self.model_dump())


class OpossumPackage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    source: SourceInfo
    attribution_confidence: int | None = None
    comment: str | None = None
    package_name: str | None = None
    package_version: str | None = None
    package_namespace: str | None = None
    package_type: str | None = None
    package_p_u_r_l_appendix: str | None = None
    copyright: str | None = None
    license_name: str | None = None
    license_text: str | None = None
    url: str | None = None
    first_party: bool | None = None
    exclude_from_notice: bool | None = None
    pre_selected: bool | None = None
    follow_up: Literal["FOLLOW_UP"] | None = None
    origin_id: str | None = None
    origin_ids: list[str] | None = None
    criticality: Literal["high"] | Literal["medium"] | None = None
    was_preferred: bool | None = None

    def to_opossum_file_format(self) -> opossum_file.OpossumPackage:
        return opossum_file.OpossumPackage(
            source=self.source.to_opossum_file_format(),
            attribution_confidence=self.attribution_confidence,
            comment=self.comment,
            package_name=self.package_name,
            package_version=self.package_version,
            package_namespace=self.package_namespace,
            package_type=self.package_type,
            package_p_u_r_l_appendix=self.package_p_u_r_l_appendix,
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


class Metadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="allow")
    project_id: str
    file_creation_date: str
    project_title: str
    project_version: str | None = None
    expected_release_date: str | None = None
    build_date: str | None = None

    def to_opossum_file_format(self) -> opossum_file.Metadata:
        return opossum_file.Metadata(**self.model_dump())


class ResourceType(Enum):
    FILE = auto()
    FOLDER = auto()


class ExternalAttributionSource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str
    priority: int
    is_relevant_for_preferred: bool | None = None

    def to_opossum_file_format(self) -> opossum_file.ExternalAttributionSource:
        return opossum_file.ExternalAttributionSource(**self.model_dump())
