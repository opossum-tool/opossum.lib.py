# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Union


@dataclass(frozen=True)
class SourceInfo:
    name: str
    documentConfidence: int


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
class OpossumInformation:
    metadata: Metadata
    resources: Dict[str, Any]
    externalAttributions: Dict[str, Any]
    resourcesToAttributions: Dict[str, List[str]]
    attributionBreakpoints: List[str]
