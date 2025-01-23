# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

# @mock.patch(
#     "opossum_lib.scancode.resource_tree.get_attribution_info",
#     autospec=True,
#     return_value=[OpossumPackage(source=SourceInfo(name="mocked"))],
# )
# def test_create_attribution_mapping_paths_have_root_prefix(_: Any) -> None:
#     rootnode = _create_reference_node_structure()
#     _, resources_to_attributions = create_attribution_mapping(rootnode)
#     # OpossumUI automatically prepends every path with a "/"
#     # So our resourcesToAttributions needs to start every path with "/"
#     # even though ScanCode paths don't start with "/".
#     assert "/A/file1" in resources_to_attributions
#     assert "/A/file2.txt" in resources_to_attributions
#     assert "/A/B/file3" in resources_to_attributions

# def test_create_attribution_mapping() -> None:
#     _, _, file1, file2, file3 = _create_reference_scancode_files()
#     pkg1 = OpossumPackage(source=SourceInfo(name="S1"))
#     pkg2 = OpossumPackage(source=SourceInfo(name="S2"))
#     pkg3 = OpossumPackage(source=SourceInfo(name="S3"))

#     def get_attribution_info_mock(file: File) -> list[OpossumPackage]:
#         if file == file1:
#             return [deepcopy(pkg1), deepcopy(pkg2)]
#         elif file == file2:
#             return [deepcopy(pkg1), deepcopy(pkg2), deepcopy(pkg3)]
#         elif file == file3:
#             return []
#         else:
#             return []

#     root_node = _create_reference_node_structure()

#     with mock.patch(
#         "opossum_lib.scancode.resource_tree.get_attribution_info",
#         new=get_attribution_info_mock,
#     ):
#         external_attributions, resources_to_attributions = create_attribution_mapping(
#             root_node
#         )
#     assert len(external_attributions) == 3  # deduplication worked

#     reverse_mapping = {v: k for (k, v) in external_attributions.items()}
#     id1,id2,id3 = reverse_mapping[pkg1], reverse_mapping[pkg2], reverse_mapping[pkg3]
#     assert len(resources_to_attributions) == 2  # only files with attributions
#     assert set(resources_to_attributions["/" + file1.path]) == {id1, id2}
#     assert set(resources_to_attributions["/" + file2.path]) == {id1, id2, id3}
