# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Any

from opossum_lib.scancode.model import File, ScanCodeData
from opossum_lib.scancode.resource_tree import (
    Node,
    convert_to_opossum_resources,
    scancode_to_resource_tree,
)


def test_scancode_to_resource_tree() -> None:
    files = _create_reference_scancode_files()
    scancode_data = ScanCodeData(
        headers=[], packages=[], dependencies=[], license_detections=[], files=files
    )

    tree = scancode_to_resource_tree(scancode_data)
    folder, subfolder, file1, file2, file3 = files
    inner = Node(file=subfolder, children={"file3": Node(file=file3)})
    reference = Node(
        file=folder,
        children={"B": inner, "file1": Node(file=file1), "file2.txt": Node(file=file2)},
    )

    assert tree == reference


def test_convert_to_opossum_resources() -> None:
    scancode_data = ScanCodeData(
        headers=[],
        packages=[],
        dependencies=[],
        license_detections=[],
        files=_create_reference_scancode_files(),
    )

    tree = scancode_to_resource_tree(scancode_data)
    resources = convert_to_opossum_resources(tree)
    reference = {"A": {"B": {"file3": 1}, "file1": 1, "file2.txt": 1}}
    assert resources.to_dict() == reference


def _create_file(path: str, type: str, **kwargs: dict[str, Any]) -> File:
    dprops = {
        "path": path,
        "type": type,
        "name": Path(path).name,
        "base_name": Path(Path(path).name).stem,
        "extension": Path(path).suffix,
        "size": 0,
        "date": None,
        "sha1": None,
        "md5": None,
        "sha256": None,
        "mime_type": None,
        "file_type": None,
        "programming_language": None,
        "is_binary": False,
        "is_text": False,
        "is_archive": False,
        "is_media": False,
        "is_source": False,
        "is_script": False,
        "package_data": [],
        "for_packages": [],
        "detected_license_expression": None,
        "detected_license_expression_spdx": None,
        "license_detections": [],  # list[LicenseDetection1]
        "license_clues": [],
        "percentage_of_license_text": 0.0,
        "copyrights": [],  # ,list[Copyright],
        "holders": [],  # list[Holder],
        "authors": [],
        "emails": [],
        "urls": [],  # list[Url],
        "files_count": 0,
        "dirs_count": 0,
        "size_count": 0,
        "scan_errors": [],
        **kwargs,
    }
    return File.model_validate(dprops)


def _create_reference_scancode_files() -> list[File]:
    return [
        _create_file("A", "folder"),
        _create_file("A/B", "folder"),
        _create_file("A/file1", "file"),
        _create_file("A/file2.txt", "file"),
        _create_file("A/B/file3", "file"),
    ]
