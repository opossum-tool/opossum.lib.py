# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import uuid
from os.path import relpath

from pydantic import BaseModel

from opossum_lib.opossum.opossum_file import (
    OpossumPackage,
    OpossumPackageIdentifier,
    Resource,
    ResourcePath,
    ResourceType,
    SourceInfo,
)
from opossum_lib.scancode.helpers import check_schema, path_segments
from opossum_lib.scancode.model import File, ScanCodeData


class Node(BaseModel):
    file: File
    children: dict[str, "Node"] = {}

    def get_path(self, path: list[str]) -> "Node":
        if len(path) == 0:
            return self
        next_segment, *rest = path
        if next_segment not in self.children:
            self.children[next_segment] = Node.model_construct(None)
        return self.children[next_segment].get_path(rest)


def scancode_to_resource_tree(scanCodeData: ScanCodeData) -> Node:
    root = Node.model_construct(None)
    for file in scanCodeData.files:
        segments = path_segments(file.path)
        root.get_path(segments).file = file

    assert len(root.children) == 1
    the_child = list(root.children.values())[0]
    check_schema(the_child)
    return the_child


def convert_to_opossum_resources(rootnode: Node) -> Resource:
    def process_node(node: Node) -> Resource:
        if node.file.type == "file":
            return Resource(ResourceType.FILE)
        else:
            rootpath = node.file.path
            children = {
                relpath(n.file.path, rootpath): process_node(n)
                for n in node.children.values()
            }
            return Resource(ResourceType.FOLDER, children)

    return Resource(
        ResourceType.TOP_LEVEL, {rootnode.file.path: process_node(rootnode)}
    )


def get_attribution_info(file: File) -> list[OpossumPackage]:
    if file.type == "directory":
        return []
    copyright = "\n".join(map(lambda c: c.copyright, file.copyrights))

    attribution_infos = []
    for license_detection in file.license_detections:
        licenseName = license_detection.license_expression_spdx
        minscore = min(map(lambda m: m.score, license_detection.matches))
        attributionConfidence = int(minscore)

        source_info = SourceInfo("SC")  # ScanCode, no confidence given
        package = OpossumPackage(
            source_info,
            licenseName=licenseName,
            attributionConfidence=attributionConfidence,
            copyright=copyright,
        )
        attribution_infos.append(package)

    return attribution_infos


def create_attribution_mapping(
    rootnode: Node,
) -> tuple[
    dict[OpossumPackageIdentifier, OpossumPackage],
    dict[ResourcePath, list[OpossumPackageIdentifier]],
]:
    attributionLookup = {}  # attribution -> uuid
    resourcesToAttributions = {}  # path -> [attributionUUID]

    def process_node(node: Node) -> None:
        path = node.file.path
        attributions = get_attribution_info(node.file)
        attributionIDs = []
        for attribution in attributions:
            if attribution not in attributionLookup:
                attributionLookup[attribution] = str(uuid.uuid4())
            attributionIDs.append(attributionLookup[attribution])
        if len(attributionIDs) > 0:
            resourcesToAttributions[path] = attributionIDs

        for child in node.children.values():
            process_node(child)

    for child in rootnode.children.values():
        process_node(child)

    # uuid -> attribution
    externalAttributions = {id: attr for (attr, id) in attributionLookup.items()}
    return externalAttributions, resourcesToAttributions
