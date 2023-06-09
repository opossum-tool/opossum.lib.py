# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Literal, Optional, Tuple, Union

OpossumPackageIdentifier = str
ResourcePath = str


@dataclass(frozen=True)
class OpossumInformation:
    metadata: Metadata
    resources: Resource
    externalAttributions: Dict[OpossumPackageIdentifier, OpossumPackage]
    resourcesToAttributions: Dict[ResourcePath, List[OpossumPackageIdentifier]]
    attributionBreakpoints: List[str] = field(default_factory=list)
    externalAttributionSources: Dict[str, ExternalAttributionSource] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SourceInfo:
    name: str
    documentConfidence: Optional[int] = 0


@dataclass(frozen=True)
class OpossumPackage:
    source: SourceInfo
    attributionConfidence: Optional[int] = None
    comment: Optional[str] = None
    packageName: Optional[str] = None
    packageVersion: Optional[str] = None
    packageNamespace: Optional[str] = None
    packageType: Optional[str] = None
    packagePURLAppendix: Optional[str] = None
    copyright: Optional[str] = None
    licenseName: Optional[str] = None
    licenseText: Optional[str] = None
    url: Optional[str] = None
    firstParty: Optional[bool] = None
    excludeFromNotice: Optional[bool] = None
    preSelected: Optional[bool] = None
    followUp: Optional[Literal["FOLLOW_UP"]] = None
    originId: Optional[str] = None
    criticality: Optional[Union[Literal["high"], Literal["medium"]]] = None


@dataclass(frozen=True)
class Metadata:
    projectId: str
    fileCreationDate: str
    projectTitle: str
    projectVersion: Optional[str] = None
    expectedReleaseDate: Optional[str] = None
    buildDate: Optional[str] = None


class ResourceType(Enum):
    FILE = auto()
    FOLDER = auto()
    TOP_LEVEL = auto()
    OTHER = auto()


@dataclass(frozen=True)
class Resource:
    type: ResourceType
    children: Dict[str, Resource] = field(default_factory=dict)

    def add_path(self, path: List[str], type_of_last_element: ResourceType) -> None:
        if len(path) == 0:
            return
        first, rest = path[0], path[1:]
        if self.leaf_element_exists_but_resource_type_differs(
            first, rest, type_of_last_element
        ):
            raise TypeError(
                "Couldn't add path to resource: ResourceType of leaf elements with"
                "the same path differ."
            )
        if first not in self.children:
            if len(rest) != 0:
                self.children[first] = Resource(type=ResourceType.FOLDER)
            else:
                self.children[first] = Resource(type=type_of_last_element)

        self.children[first].add_path(rest, type_of_last_element)

    def leaf_element_exists_but_resource_type_differs(
        self, first: str, rest: List[str], type_of_last_element: ResourceType
    ) -> bool:
        return (
            first in self.children
            and len(self.children[first].children) == 0
            and len(rest) == 0
            and self.type != type_of_last_element
        )

    def to_dict(self) -> Union[int, Dict]:
        if len(self.children) == 0:
            if self.type == ResourceType.FILE:
                return 1
            elif self.type == ResourceType.FOLDER:
                return {}
            else:
                return 1
        else:
            return {
                name: resource.to_dict() for name, resource in self.children.items()
            }

    def get_paths(self) -> List[Tuple[str, ResourceType]]:
        if len(self.children) == 0:
            if self.type == ResourceType.FOLDER:
                return [("/", self.type)]
            elif self.type == ResourceType.FILE:
                return [("", self.type)]
            else:
                return [("", self.type)]
        paths = []
        for name, resource in self.children.items():
            path = [
                ("/" + name + path, resource_type)
                for (path, resource_type) in resource.get_paths()
            ]
            paths.extend(path)
        return paths


@dataclass(frozen=True)
class ExternalAttributionSource:
    name: str
    priority: int
