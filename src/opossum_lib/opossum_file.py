# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Union

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


@dataclass(frozen=True)
class Resource:
    children: Dict[str, Resource] = field(default_factory=dict)

    def add_path(self, path: List[str]) -> None:
        if len(path) == 0:
            return
        first, rest = path[0], path[1:]
        if first not in self.children:
            self.children[first] = Resource()
        self.children[first].add_path(rest)

    def to_dict(self) -> Union[int, Dict]:
        if len(self.children) == 0:
            return 1
        else:
            return {
                name: resource.to_dict() for name, resource in self.children.items()
            }

    def get_paths(self) -> List[str]:
        if len(self.children) == 0:
            return ["/"]
        paths = []
        for name, resource in self.children.items():
            path = ["/" + name + path for path in resource.get_paths()]
            paths.extend(path)
        return paths


@dataclass(frozen=True)
class ExternalAttributionSource:
    name: str
    priority: int
