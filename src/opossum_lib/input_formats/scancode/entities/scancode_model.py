# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class OptionsModel(BaseModel, extra="ignore"):
    input: list[str]


class SystemEnvironmentModel(BaseModel):
    cpu_architecture: str
    operating_system: str
    platform: str
    platform_version: str
    python_version: str


class ExtraDataModel(BaseModel):
    files_count: int
    spdx_license_list_version: str
    system_environment: SystemEnvironmentModel


class HeaderModel(BaseModel):
    duration: float
    end_timestamp: str
    errors: list
    extra_data: ExtraDataModel
    message: Any
    notice: str
    options: OptionsModel
    output_format_version: str
    start_timestamp: str
    tool_name: str
    tool_version: str
    warnings: list


class ReferenceMatchModel(BaseModel):
    end_line: int
    from_file: str
    license_expression: str
    license_expression_spdx: str
    matched_length: int
    matcher: str
    match_coverage: float
    rule_identifier: str
    rule_relevance: int
    rule_url: Any
    score: float
    start_line: int


class MatchModel(BaseModel):
    end_line: int
    from_file: str
    license_expression: str
    license_expression_spdx: str
    matched_length: int
    matcher: str
    match_coverage: float
    rule_identifier: str
    rule_relevance: int
    rule_url: Any
    score: float
    start_line: int


class GlobalLicenseDetectionModel(BaseModel):
    detection_count: int
    identifier: str
    license_expression: str
    license_expression_spdx: str
    reference_matches: list[ReferenceMatchModel]


class FileBasedLicenseDetectionModel(BaseModel):
    license_expression: str
    license_expression_spdx: str
    matches: list[MatchModel]
    identifier: str


class CopyrightModel(BaseModel):
    copyright: str
    end_line: int
    start_line: int


class HolderModel(BaseModel):
    end_line: int
    holder: str
    start_line: int


class UrlModel(BaseModel):
    end_line: int
    start_line: int
    url: str


class EmailModel(BaseModel):
    email: str
    end_line: int
    start_line: int


class FileTypeModel(Enum):
    FILE = "file"
    DIRECTORY = "directory"


class FileModel(BaseModel):
    authors: list
    base_name: str
    copyrights: list[CopyrightModel]
    date: str | None
    detected_license_expression: str | None
    detected_license_expression_spdx: str | None
    dirs_count: int
    emails: list[EmailModel]
    extension: str
    files_count: int
    file_type: str | None
    for_packages: list
    holders: list[HolderModel]
    is_archive: bool
    is_binary: bool
    is_media: bool
    is_script: bool
    is_source: bool
    is_text: bool
    license_clues: list
    license_detections: list[FileBasedLicenseDetectionModel]
    md5: str | None
    mime_type: str | None
    name: str
    package_data: list
    path: str
    percentage_of_license_text: float
    programming_language: str | None
    scan_errors: list
    sha1: str | None
    sha256: str | None
    size: int
    size_count: int
    type: FileTypeModel
    urls: list[UrlModel]


class ScancodeModel(BaseModel):
    dependencies: list
    files: list[FileModel]
    license_detections: list[GlobalLicenseDetectionModel]
    headers: list[HeaderModel]
    packages: list
