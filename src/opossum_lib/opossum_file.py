# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Literal

OpossumPackageIdentifier = str
ResourcePath = str


@dataclass(frozen=True)
class OpossumInformation:
    metadata: Metadata
    resources: Resource
    externalAttributions: dict[OpossumPackageIdentifier, OpossumPackage]
    resourcesToAttributions: dict[ResourcePath, list[OpossumPackageIdentifier]]
    attributionBreakpoints: list[str] = field(default_factory=list)
    externalAttributionSources: dict[str, ExternalAttributionSource] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SourceInfo:
    name: str
    documentConfidence: int | None = 0


@dataclass(frozen=True)
class OpossumPackage:
    source: SourceInfo
    attributionConfidence: int | None = None
    comment: str | None = None
    packageName: str | None = None
    packageVersion: str | None = None
    packageNamespace: str | None = None
    packageType: str | None = None
    packagePURLAppendix: str | None = None
    copyright: str | None = None
    licenseName: str | None = None
    licenseText: str | None = None
    url: str | None = None
    firstParty: bool | None = None
    excludeFromNotice: bool | None = None
    preSelected: bool | None = None
    followUp: Literal["FOLLOW_UP"] | None = None
    originId: str | None = None
    criticality: Literal["high"] | Literal["medium"] | None = None


@dataclass(frozen=True)
class Metadata:
    projectId: str
    fileCreationDate: str
    projectTitle: str
    projectVersion: str | None = None
    expectedReleaseDate: str | None = None
    buildDate: str | None = None


class ResourceType(Enum):
    FILE = auto()
    FOLDER = auto()
    TOP_LEVEL = auto()
    OTHER = auto()


@dataclass(frozen=True)
class Resource:
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
            resource = Resource(ResourceType.TOP_LEVEL)
            paths_in_resource.remove(path_to_element_to_drop)
            paths_in_resource.append(path_to_element_to_drop[:-1])

            for path_to_element_to_drop in paths_in_resource:
                resource = resource.add_path(path_to_element_to_drop)

            return resource

    def to_dict(self) -> int | dict:
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


@dataclass(frozen=True)
class ExternalAttributionSource:
    name: str
    priority: int
