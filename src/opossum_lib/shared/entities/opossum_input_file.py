# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from copy import deepcopy
from dataclasses import field
from enum import Enum, auto
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_serializer
from pydantic.alias_generators import to_camel

type OpossumPackageIdentifier = str
type ResourcePath = str
type ResourceInFile = dict[str, ResourceInFile] | int


class CamelBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="forbid", frozen=True
    )


class OpossumInputFile(CamelBaseModel):
    metadata: Metadata
    resources: ResourceInFile
    external_attributions: dict[OpossumPackageIdentifier, OpossumPackage]
    resources_to_attributions: dict[ResourcePath, list[OpossumPackageIdentifier]]
    attribution_breakpoints: list[str] = field(default_factory=list)
    external_attribution_sources: dict[str, ExternalAttributionSource] = field(
        default_factory=dict
    )
    frequent_licenses: list[FrequentLicense] | None = None
    files_with_children: list[str] | None = None
    base_urls_for_sources: BaseUrlsForSources | None = None


class BaseUrlsForSources(CamelBaseModel):
    @model_serializer
    def serialize(self) -> dict:
        # hack to override not serializing keys with corresponding value none:
        # In this case this is valid and should be part of the serialization
        return {k: v for k, v in self}

    model_config = ConfigDict(extra="allow")


class FrequentLicense(CamelBaseModel):
    full_name: str
    short_name: str
    default_text: str


class SourceInfo(CamelBaseModel):
    name: str
    document_confidence: int | float | None = 0
    additional_name: str | None = None


class OpossumPackage(CamelBaseModel):
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


class Metadata(CamelBaseModel):
    model_config = ConfigDict(extra="allow")
    project_id: str
    file_creation_date: str
    project_title: str
    project_version: str | None = None
    expected_release_date: str | None = None
    build_date: str | None = None


class ResourceType(Enum):
    FILE = auto()
    FOLDER = auto()
    TOP_LEVEL = auto()
    OTHER = auto()


class Resource(CamelBaseModel):
    type: ResourceType
    children: dict[str, Resource] = field(default_factory=dict)

    def add_path(
        self, path_with_resource_types: list[tuple[str, ResourceType]]
    ) -> Resource:
        resource = deepcopy(self)
        if len(path_with_resource_types) == 0:
            return resource
        (first, resource_type), rest = (
            path_with_resource_types[0],
            path_with_resource_types[1:],
        )
        if self.element_exists_but_resource_type_differs(first, resource_type):
            raise TypeError(
                "Couldn't add path to resource: ResourceType of elements with"
                " the same path differ."
            )
        if first not in self.children:
            resource.children[first] = Resource(type=resource_type)
        resource.children[first] = resource.children[first].add_path(rest)

        return resource

    def element_exists_but_resource_type_differs(
        self, element: str, resource_type: ResourceType
    ) -> bool:
        if element in self.children:
            return self.children[element].type != resource_type
        return False

    def drop_element(
        self, path_to_element_to_drop: list[tuple[str, ResourceType]]
    ) -> Resource:
        paths_in_resource = self.get_paths_of_all_leaf_nodes_with_types()
        if path_to_element_to_drop not in paths_in_resource:
            raise ValueError(
                f"Element {path_to_element_to_drop} doesn't exist in resource!"
            )

        else:
            resource = Resource(type=ResourceType.TOP_LEVEL)
            paths_in_resource.remove(path_to_element_to_drop)
            paths_in_resource.append(path_to_element_to_drop[:-1])

            for path_to_element_to_drop in paths_in_resource:
                resource = resource.add_path(path_to_element_to_drop)

            return resource

    def to_dict(self) -> ResourceInFile:
        if not self.has_children():
            if self.type == ResourceType.FOLDER:
                return {}
            else:
                return 1
        else:
            return {
                name: resource.to_dict() for name, resource in self.children.items()
            }

    def get_paths_of_all_leaf_nodes_with_types(
        self,
    ) -> list[list[tuple[str, ResourceType]]]:
        paths = []
        for name, resource in self.children.items():
            path = [(name, resource.type)]
            if resource.has_children():
                paths.extend(
                    [
                        path + element
                        for element in resource.get_paths_of_all_leaf_nodes_with_types()
                    ]
                )
            else:
                paths.extend([path])
        return paths

    def has_children(self) -> bool:
        return len(self.children) > 0

    def convert_to_file_resource(self) -> ResourceInFile:
        return self.to_dict()


class ExternalAttributionSource(CamelBaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    priority: int
    is_relevant_for_preferred: bool | None = None
