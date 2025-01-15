# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


from os.path import relpath

from pydantic import BaseModel

from opossum_lib.opossum.opossum_file import (
    OpossumPackage,
    OpossumPackageIdentifier,
    ResourceInFile,
    ResourcePath,
    SourceInfo,
)
from opossum_lib.scancode.helpers import check_schema, path_segments
from opossum_lib.scancode.model import File, ScanCodeData


class ScanCodeFileTree(BaseModel):
    file: File
    children: dict[str, "ScanCodeFileTree"] = {}

    def get_path(self, path: list[str]) -> "ScanCodeFileTree":
        if len(path) == 0:
            return self
        next_segment, *rest = path
        if next_segment not in self.children:
            self.children[next_segment] = ScanCodeFileTree.model_construct(None)
        return self.children[next_segment].get_path(rest)

    def revalidate(self) -> None:
        check_schema(self)
        for child in self.children.values():
            child.revalidate()


def scancode_to_file_tree(scanCodeData: ScanCodeData) -> ScanCodeFileTree:
    root = ScanCodeFileTree.model_construct(file=None)
    for file in scanCodeData.files:
        segments = path_segments(file.path)
        root.get_path(segments).file = file

    assert len(root.children) == 1
    the_child = list(root.children.values())[0]
    check_schema(the_child)
    return the_child


def convert_to_opossum_resources(rootnode: ScanCodeFileTree) -> ResourceInFile:
    def process_node(node: ScanCodeFileTree) -> ResourceInFile:
        if node.file.type == "file":
            return 1
        else:
            rootpath = node.file.path
            children = {
                relpath(n.file.path, rootpath): process_node(n)
                for n in node.children.values()
            }
            return children

    return {rootnode.file.path: process_node(rootnode)}


def get_attribution_info(file: File) -> list[OpossumPackage]:
    if file.type == "directory":
        return []
    copyright = "\n".join(map(lambda c: c.copyright, file.copyrights))
    source_info = SourceInfo("SC")  # ScanCode, no confidence given

    attribution_infos = []
    for license_detection in file.license_detections:
        licenseName = license_detection.license_expression_spdx
        maxscore = max(map(lambda m: m.score, license_detection.matches))
        attributionConfidence = int(maxscore)

        package = OpossumPackage(
            source_info,
            licenseName=licenseName,
            attributionConfidence=attributionConfidence,
            copyright=copyright,
        )
        attribution_infos.append(package)

    return attribution_infos


def create_attribution_mapping(
    rootnode: ScanCodeFileTree,
) -> tuple[
    dict[OpossumPackageIdentifier, OpossumPackage],
    dict[ResourcePath, list[OpossumPackageIdentifier]],
]:
    attributionLookup = {}  # attribution -> uuid
    resourcesToAttributions = {}  # path -> [attributionUUID]

    def process_node(node: ScanCodeFileTree) -> None:
        # the / is required by OpossumUI
        path = "/" + node.file.path
        attributions = get_attribution_info(node.file)
        attributionIDs = []
        for attribution in attributions:
            if attribution not in attributionLookup:
                attributionLookup[attribution] = (
                    f"{attribution.licenseName}-{hash(attribution)}"
                )
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
