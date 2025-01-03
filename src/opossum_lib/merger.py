# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from opossum_lib.opossum_file import (
    OpossumInformation,
    OpossumPackageIdentifier,
    Resource,
    ResourcePath,
    ResourceType,
)


def merge_opossum_information(
    elements_to_merge: list[OpossumInformation],
) -> OpossumInformation:
    expanded_opossum_information = [
        expand_opossum_package_identifier(opossum_information)
        for opossum_information in elements_to_merge
    ]
    return OpossumInformation(
        metadata=expanded_opossum_information[0].metadata,
        resources=_merge_resources(
            [
                opossum_information.resources
                for opossum_information in expanded_opossum_information
            ]
        ),
        externalAttributions=_merge_dicts_without_duplicates(
            [
                opossum_information.externalAttributions
                for opossum_information in expanded_opossum_information
            ]
        ),
        resourcesToAttributions=_merge_resources_to_attributions(
            [
                opossum_information.resourcesToAttributions
                for opossum_information in expanded_opossum_information
            ]
        ),
        attributionBreakpoints=_merge_attribution_breakpoints(
            [
                opossum_information.attributionBreakpoints
                for opossum_information in expanded_opossum_information
            ]
        ),
        externalAttributionSources=_merge_dicts_without_duplicates(
            [
                opossum_information.externalAttributionSources
                for opossum_information in expanded_opossum_information
            ]
        ),
    )


def expand_opossum_package_identifier(
    opossum_information: OpossumInformation,
) -> OpossumInformation:
    """IDs for the attributions should be unique per OpossumInformation.
    To prevent possible duplicates we add the projectId of the
    OpossumInformation to the IDs as a prefix."""
    prefix = opossum_information.metadata.projectId
    extended_resources_to_attributions = dict()
    for (
        resource_path,
        identifiers,
    ) in opossum_information.resourcesToAttributions.items():
        extended_resources_to_attributions[resource_path] = [
            prefix + "-" + identifier for identifier in identifiers
        ]
    extended_external_attributions = dict()
    for (
        identifier,
        external_attribution,
    ) in opossum_information.externalAttributions.items():
        extended_external_attributions[prefix + "-" + identifier] = external_attribution

    return OpossumInformation(
        metadata=opossum_information.metadata,
        resources=opossum_information.resources,
        externalAttributions=extended_external_attributions,
        resourcesToAttributions=extended_resources_to_attributions,
        attributionBreakpoints=opossum_information.attributionBreakpoints,
        externalAttributionSources=opossum_information.externalAttributionSources,
    )


def _merge_resources(resources: list[Resource]) -> Resource:
    merged_resource = Resource(ResourceType.TOP_LEVEL)
    for resource in resources:
        for path in resource.get_paths_of_all_leaf_nodes_with_types():
            merged_resource = merged_resource.add_path(path)
    return merged_resource


def _merge_resources_to_attributions(
    resources_to_attributions: list[dict[ResourcePath, list[OpossumPackageIdentifier]]],
) -> dict[ResourcePath, list[OpossumPackageIdentifier]]:
    merged_resources_to_attributions: dict[
        ResourcePath, list[OpossumPackageIdentifier]
    ] = dict()
    for resource_to_attribution in resources_to_attributions:
        for resource_path, identifiers in resource_to_attribution.items():
            identifiers_merged = merged_resources_to_attributions.get(resource_path, [])
            identifiers_merged.extend(
                [idf for idf in identifiers if idf not in identifiers_merged]
            )
            merged_resources_to_attributions[resource_path] = identifiers_merged

    return merged_resources_to_attributions


def _merge_attribution_breakpoints(
    attribution_breakpoints_to_merge: list[list[str]],
) -> list[str]:
    merged_attribution_breakpoints = []
    for attribution_breakpoints in attribution_breakpoints_to_merge:
        merged_attribution_breakpoints.extend(
            [
                attribution_breakpoint
                for attribution_breakpoint in attribution_breakpoints
                if attribution_breakpoint not in merged_attribution_breakpoints
            ]
        )
    return merged_attribution_breakpoints


def _merge_dicts_without_duplicates(dicts: list[dict[str, Any]]) -> dict[str, Any]:
    merged_dict: dict[str, Any] = dict()
    for single_dict in dicts:
        for key, value in single_dict.items():
            if key in merged_dict and merged_dict.get(key) != value:
                raise TypeError(
                    "Couldn't merge and deduplicate: "
                    "Values for identical keys don't match."
                )
            merged_dict.update({key: value})
    return merged_dict
