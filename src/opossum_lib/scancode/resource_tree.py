# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

from pydantic import BaseModel

import opossum_lib.opossum_model as opossum_model
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

    def to_opossum_resources(
        self,
    ) -> list[opossum_model.Resource]:
        def process_node(
            node: ScanCodeFileTree,
        ) -> opossum_model.Resource:
            return opossum_model.Resource(
                path=node.file.path,
                attributions=get_attribution_info(node.file),
                type=convert_resource_type(node.file.type),
                children=[process_node(child) for child in node.children.values()],
            )

        return [process_node(self)]


def scancode_to_file_tree(scancode_data: ScanCodeData) -> ScanCodeFileTree:
    temp_root = ScanCodeFileTree.model_construct(file=None)  # type: ignore
    for file in scancode_data.files:
        segments = path_segments(file.path)
        temp_root.get_path(segments).file = file

    assert len(temp_root.children) == 1
    root = list(temp_root.children.values())[0]
    check_schema(root)
    return root


def get_attribution_info(file: File) -> list[opossum_model.OpossumPackage]:
    if file.type == FileType.DIRECTORY:
        return []
    copyright = "\n".join(c.copyright for c in file.copyrights)
    source_info = opossum_model.SourceInfo(name=SCANCODE_SOURCE_NAME)

    attribution_infos = []
    for license_detection in file.license_detections:
        license_name = license_detection.license_expression_spdx
        max_score = max(m.score for m in license_detection.matches)
        attribution_confidence = int(max_score)

        package = opossum_model.OpossumPackage(
            source=source_info,
            license_name=license_name,
            attribution_confidence=attribution_confidence,
            copyright=copyright,
        )
        attribution_infos.append(package)

    return attribution_infos


def convert_resource_type(val: FileType) -> opossum_model.ResourceType:
    if val == FileType.FILE:
        return opossum_model.ResourceType.FILE
    else:
        return opossum_model.ResourceType.FOLDER
