# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

from os.path import relpath

from pydantic import BaseModel

from opossum_lib.opossum.opossum_file import (
    OpossumPackage,
    OpossumPackageIdentifier,
    ResourceInFile,
    ResourcePath,
    SourceInfo,
)
from opossum_lib.scancode.constants import SCANCODE_SOURCE_NAME
from opossum_lib.scancode.helpers import check_schema, path_segments
from opossum_lib.scancode.model import File, FileType, ScanCodeData


class ScanCodeFileTree(BaseModel):
    file: File
    children: dict[str, ScanCodeFileTree] = {}

    def get_path(self, path: list[str]) -> ScanCodeFileTree:
        if len(path) == 0:
            return self
        next_segment, *rest = path
        if next_segment not in self.children:
            self.children[next_segment] = ScanCodeFileTree.model_construct(None)  # type: ignore
        return self.children[next_segment].get_path(rest)

    def revalidate(self) -> None:
        check_schema(self)
        for child in self.children.values():
            child.revalidate()


def scancode_to_file_tree(scancode_data: ScanCodeData) -> ScanCodeFileTree:
    temp_root = ScanCodeFileTree.model_construct(file=None)  # type: ignore
    for file in scancode_data.files:
        segments = path_segments(file.path)
        temp_root.get_path(segments).file = file

    assert len(temp_root.children) == 1
    root = list(temp_root.children.values())[0]
    check_schema(root)
    return root


def convert_to_opossum_resources(root_node: ScanCodeFileTree) -> ResourceInFile:
    def process_node(node: ScanCodeFileTree) -> ResourceInFile:
        if node.file.type == FileType.FILE:
            return 1
        else:
            root_path = node.file.path
            children = {
                relpath(n.file.path, root_path): process_node(n)
                for n in node.children.values()
            }
            return children

    return {root_node.file.path: process_node(root_node)}


def get_attribution_info(file: File) -> list[OpossumPackage]:
    if file.type == FileType.DIRECTORY:
        return []
    copyright = "\n".join(c.copyright for c in file.copyrights)
    source_info = SourceInfo(SCANCODE_SOURCE_NAME)

    attribution_infos = []
    for license_detection in file.license_detections:
        license_name = license_detection.license_expression_spdx
        max_score = max(m.score for m in license_detection.matches)
        attribution_confidence = int(max_score)

        package = OpossumPackage(
            source_info,
            licenseName=license_name,
            attributionConfidence=attribution_confidence,
            copyright=copyright,
        )
        attribution_infos.append(package)

    return attribution_infos


def get_attribution_key(attribution: OpossumPackage) -> OpossumPackageIdentifier:
    return f"{attribution.licenseName}-{hash(attribution)}"


def create_attribution_mapping(
    root_node: ScanCodeFileTree,
) -> tuple[
    dict[OpossumPackageIdentifier, OpossumPackage],
    dict[ResourcePath, list[OpossumPackageIdentifier]],
]:
    external_attributions: dict[OpossumPackageIdentifier, OpossumPackage] = {}
    resources_to_attributions: dict[ResourcePath, list[OpossumPackageIdentifier]] = {}

    def process_node(node: ScanCodeFileTree) -> None:
        # the / is required by OpossumUI
        path = "/" + node.file.path
        attributions = get_attribution_info(node.file)

        new_attributions_with_id = {get_attribution_key(a): a for a in attributions}
        external_attributions.update(new_attributions_with_id)

        if len(new_attributions_with_id) > 0:
            resources_to_attributions[path] = list(new_attributions_with_id.keys())

        for child in node.children.values():
            process_node(child)

    for child in root_node.children.values():
        process_node(child)

    return external_attributions, resources_to_attributions
