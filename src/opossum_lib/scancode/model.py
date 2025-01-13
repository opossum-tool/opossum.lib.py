# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Options(BaseModel, extra="ignore"):
    input: list[str]


class SystemEnvironment(BaseModel):
    operating_system: str
    cpu_architecture: str
    platform: str
    platform_version: str
    python_version: str


class ExtraData(BaseModel):
    system_environment: SystemEnvironment
    spdx_license_list_version: str
    files_count: int


class Header(BaseModel):
    tool_name: str
    tool_version: str
    options: Options
    notice: str
    start_timestamp: str
    end_timestamp: str
    output_format_version: str
    duration: float
    message: Any
    errors: list
    warnings: list
    extra_data: ExtraData


class ReferenceMatch(BaseModel):
    license_expression: str
    license_expression_spdx: str
    from_file: str
    start_line: int
    end_line: int
    matcher: str
    score: float
    matched_length: int
    match_coverage: float
    rule_relevance: int
    rule_identifier: str
    rule_url: Any


class LicenseDetection(BaseModel):
    identifier: str
    license_expression: str
    license_expression_spdx: str
    detection_count: int
    reference_matches: list[ReferenceMatch]


class Match(BaseModel):
    license_expression: str
    license_expression_spdx: str
    from_file: str
    start_line: int
    end_line: int
    matcher: str
    score: float
    matched_length: int
    match_coverage: float
    rule_relevance: int
    rule_identifier: str
    rule_url: Any


class LicenseDetection1(BaseModel):
    license_expression: str
    license_expression_spdx: str
    matches: list[Match]
    identifier: str


class Copyright(BaseModel):
    copyright: str
    start_line: int
    end_line: int


class Holder(BaseModel):
    holder: str
    start_line: int
    end_line: int


class Url(BaseModel):
    url: str
    start_line: int
    end_line: int


class File(BaseModel):
    path: str
    type: str
    name: str
    base_name: str
    extension: str
    size: int
    date: str | None
    sha1: str | None
    md5: str | None
    sha256: str | None
    mime_type: str | None
    file_type: str | None
    programming_language: str | None
    is_binary: bool
    is_text: bool
    is_archive: bool
    is_media: bool
    is_source: bool
    is_script: bool
    package_data: list
    for_packages: list
    detected_license_expression: str | None
    detected_license_expression_spdx: str | None
    license_detections: list[LicenseDetection1]
    license_clues: list
    percentage_of_license_text: float
    copyrights: list[Copyright]
    holders: list[Holder]
    authors: list
    emails: list
    urls: list[Url]
    files_count: int
    dirs_count: int
    size_count: int
    scan_errors: list


class ScanCodeData(BaseModel):
    headers: list[Header]
    packages: list
    dependencies: list
    license_detections: list[LicenseDetection]
    files: list[File]
