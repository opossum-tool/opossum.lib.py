# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from opossum_lib.scancode.model import (
    Copyright,
    File,
    FileBasedLicenseDetection,
    FileType,
    Holder,
    Url,
)


def _create_file(
    path: str,
    type: FileType,
    *,
    name: str | None = None,
    base_name: str | None = None,
    extension: str | None = None,
    size: int = 0,
    date: str | None = None,
    sha1: str | None = None,
    md5: str | None = None,
    sha256: str | None = None,
    mime_type: str | None = None,
    file_type: str | None = None,
    programming_language: str | None = None,
    is_binary: bool = False,
    is_text: bool = False,
    is_archive: bool = False,
    is_media: bool = False,
    is_source: bool = False,
    is_script: bool = False,
    package_data: list | None = None,
    for_packages: list | None = None,
    detected_license_expression: str | None = None,
    detected_license_expression_spdx: str | None = None,
    license_detections: list[FileBasedLicenseDetection] | None = None,
    license_clues: list | None = None,
    percentage_of_license_text: float = 0.0,
    copyrights: list[Copyright] | None = None,
    holders: list[Holder] | None = None,
    authors: list | None = None,
    emails: list | None = None,
    urls: list[Url] | None = None,
    files_count: int = 0,
    dirs_count: int = 0,
    size_count: int = 0,
    scan_errors: list | None = None,
) -> File:
    if package_data is None:
        package_data = []
    if for_packages is None:
        for_packages = []
    if license_clues is None:
        license_clues = []
    if license_detections is None:
        license_detections = []
    if scan_errors is None:
        scan_errors = []
    if urls is None:
        urls = []
    if emails is None:
        emails = []
    if authors is None:
        authors = []
    if holders is None:
        holders = []
    if copyrights is None:
        copyrights = []
    if name is None:
        name = Path(path).name
    if base_name is None:
        base_name = Path(Path(path).name).stem
    if extension is None:
        extension = Path(path).suffix
    return File(
        authors=authors,
        base_name=base_name,
        copyrights=copyrights,
        date=date,
        detected_license_expression=detected_license_expression,
        detected_license_expression_spdx=detected_license_expression_spdx,
        dirs_count=dirs_count,
        emails=emails,
        extension=extension,
        files_count=files_count,
        file_type=file_type,
        for_packages=for_packages,
        holders=holders,
        is_archive=is_archive,
        is_binary=is_binary,
        is_media=is_media,
        is_script=is_script,
        is_source=is_source,
        is_text=is_text,
        license_clues=license_clues,
        license_detections=license_detections,
        md5=md5,
        mime_type=mime_type,
        name=name,
        package_data=package_data,
        path=path,
        percentage_of_license_text=percentage_of_license_text,
        programming_language=programming_language,
        scan_errors=scan_errors,
        sha1=sha1,
        sha256=sha256,
        size=size,
        size_count=size_count,
        type=type,
        urls=urls,
    )
