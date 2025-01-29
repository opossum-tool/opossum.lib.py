# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from copy import deepcopy
from pathlib import PurePath

import opossum_lib.shared.entities.opossum_input_file as opossum_file_package
from opossum_lib.core.entities.opossum import (
    BaseUrlsForSources,
    ExternalAttributionSource,
    FrequentLicense,
    Metadata,
    Opossum,
    OpossumPackage,
    OpossumPackageIdentifier,
    Resource,
    ResourceType,
    ScanResults,
    SourceInfo,
    _convert_path_to_str,
)
from opossum_lib.shared.entities.opossum_file import OpossumFileModel
from opossum_lib.shared.entities.opossum_input_file import (
    ExternalAttributionSource as FileExternalAttributionSource,
)
from opossum_lib.shared.entities.opossum_input_file import OpossumInputFile


class OpossumFileToOpossumConverter:
    @staticmethod
    def convert_to_opossum(opossum_file: OpossumFileModel) -> Opossum:
        opossum = Opossum(
            scan_results=OpossumFileToOpossumConverter._convert_to_opossum_scan_results(
                opossum_file.input_file
            ),
            review_results=opossum_file.output_file,
        )
        return opossum

    @staticmethod
    def _convert_to_opossum_scan_results(
        opossum_information: OpossumInputFile,
    ) -> ScanResults:
        resources, used_attribution_ids = (
            OpossumFileToOpossumConverter._convert_to_opossum_model_resource_tree(
                resources=opossum_information.resources,
                external_attributions=opossum_information.external_attributions,
                resources_to_attributions=opossum_information.resources_to_attributions,
            )
        )
        # fmt: off
        frequent_licenses = (
            opossum_information.frequent_licenses
            and OpossumFileToOpossumConverter
            ._convert_frequent_licenses_to_model_frequent_licenses(
                opossum_information.frequent_licenses
            )
        )
        # fmt: on

        base_urls_for_sources = (
            opossum_information.base_urls_for_sources
            and BaseUrlsForSources(
                **(opossum_information.base_urls_for_sources.model_dump())
            )
        )

        file_attribution_sources = opossum_information.external_attribution_sources
        external_attribution_sources = {
            name: OpossumFileToOpossumConverter._convert_external_attribution_source(
                attribution_source
            )
            for name, attribution_source in file_attribution_sources.items()
        }

        attribution_with_id = (
            OpossumFileToOpossumConverter._convert_to_attribution_with_id(
                opossum_information.external_attributions
            )
        )
        return ScanResults(
            metadata=OpossumFileToOpossumConverter._convert_to_opossum_model_metadata(
                opossum_information.metadata
            ),
            resources=resources,
            attribution_breakpoints=deepcopy(
                opossum_information.attribution_breakpoints
            ),
            external_attribution_sources=external_attribution_sources,
            frequent_licenses=frequent_licenses,
            files_with_children=deepcopy(opossum_information.files_with_children),
            base_urls_for_sources=base_urls_for_sources,
            attribution_to_id=attribution_with_id,
            unassigned_attributions=OpossumFileToOpossumConverter._get_unassigned_attributions(
                used_attribution_ids, opossum_information.external_attributions
            ),
        )

    @staticmethod
    def _get_unassigned_attributions(
        used_attribution_ids: set[OpossumPackageIdentifier],
        external_attributions: dict[
            opossum_file_package.OpossumPackageIdentifier,
            opossum_file_package.OpossumPackage,
        ],
    ) -> list[OpossumPackage] | None:
        available_attribution_ids = external_attributions.keys()
        unused_attributions_ids = set(available_attribution_ids) - used_attribution_ids
        unused_attributions = [
            OpossumFileToOpossumConverter._convert_package(external_attributions[id])
            for id in unused_attributions_ids
        ]
        return unused_attributions

    @staticmethod
    def _convert_external_attribution_source(
        external_attribution_source: FileExternalAttributionSource,
    ) -> ExternalAttributionSource:
        return ExternalAttributionSource(
            name=external_attribution_source.name,
            priority=external_attribution_source.priority,
            is_relevant_for_preferred=external_attribution_source.is_relevant_for_preferred,
        )

    @staticmethod
    def _convert_frequent_licenses_to_model_frequent_licenses(
        frequent_licenses_infile: list[opossum_file_package.FrequentLicense],
    ) -> list[FrequentLicense]:
        frequent_licenses: list[FrequentLicense] = [
            OpossumFileToOpossumConverter._convert_frequent_license(license)
            for license in frequent_licenses_infile
        ]
        return frequent_licenses

    @staticmethod
    def _convert_to_opossum_model_metadata(
        infile_metadata: opossum_file_package.Metadata,
    ) -> Metadata:
        return Metadata(**infile_metadata.model_dump())

    @staticmethod
    def _convert_to_opossum_model_resource_tree(
        resources: opossum_file_package.ResourceInFile,
        external_attributions: dict[
            opossum_file_package.OpossumPackageIdentifier,
            opossum_file_package.OpossumPackage,
        ],
        resources_to_attributions: dict[
            opossum_file_package.ResourcePath,
            list[opossum_file_package.OpossumPackageIdentifier],
        ],
    ) -> tuple[list[Resource], set[OpossumPackageIdentifier]]:
        used_attribution_ids = set()

        def generate_child_resource(
            current_path: PurePath,
            to_insert: opossum_file_package.ResourceInFile,
        ) -> Resource:
            path = current_path
            current_path_as_string = _convert_path_to_str(current_path)
            if not current_path_as_string.startswith("/"):
                current_path_as_string = "/" + current_path_as_string
            attributions, attribution_ids = _get_applicable_attributions(
                current_path_as_string
            )
            used_attribution_ids.update(attribution_ids)
            if isinstance(to_insert, int):
                resource_type = ResourceType.FILE
                return Resource(
                    type=resource_type,
                    path=path,
                    attributions=attributions,
                )
            else:
                resource_type = ResourceType.FOLDER
                return Resource(
                    type=resource_type,
                    path=path,
                    attributions=attributions,
                    children={
                        relative_path: generate_child_resource(
                            current_path / relative_path, child
                        )
                        for relative_path, child in to_insert.items()
                    },
                )

        def _get_applicable_attributions(
            current_path_as_string: str,
        ) -> tuple[list[OpossumPackage], set[OpossumPackageIdentifier]]:
            attributions = []
            attribution_ids: list[str] = []
            if current_path_as_string in resources_to_attributions:
                attribution_ids = resources_to_attributions[current_path_as_string]
                attributions = [
                    OpossumFileToOpossumConverter._convert_package(
                        external_attributions[id]
                    )
                    for id in attribution_ids
                ]
            return attributions, set(attribution_ids)

        root_path = PurePath("")

        if isinstance(resources, dict):
            return [
                generate_child_resource(root_path / relative_path, child)
                for relative_path, child in resources.items()
            ], used_attribution_ids
        else:
            raise RuntimeError("Root node must not be of file type")

    @staticmethod
    def _convert_to_attribution_with_id(
        external_attributions: dict[
            opossum_file_package.OpossumPackageIdentifier,
            opossum_file_package.OpossumPackage,
        ],
    ) -> dict[OpossumPackage, str]:
        result = {}
        for package_identifier, package in external_attributions.items():
            converted_package = OpossumFileToOpossumConverter._convert_package(package)
            if converted_package not in result:
                result[converted_package] = package_identifier
            else:
                raise RuntimeError(
                    "An attribution was duplicated in the "
                    "scan breaking internal assertions"
                )
        return result

    @staticmethod
    def _convert_frequent_license(
        infile_frequent_license: opossum_file_package.FrequentLicense,
    ) -> FrequentLicense:
        return FrequentLicense(
            full_name=infile_frequent_license.full_name,
            short_name=infile_frequent_license.short_name,
            default_text=infile_frequent_license.default_text,
        )

    @staticmethod
    def _convert_package(
        infile_package: opossum_file_package.OpossumPackage,
    ) -> OpossumPackage:
        return OpossumPackage(
            source=OpossumFileToOpossumConverter._convert_source(infile_package.source),
            attribution_confidence=infile_package.attribution_confidence,
            comment=infile_package.comment,
            package_name=infile_package.package_name,
            package_version=infile_package.package_version,
            package_namespace=infile_package.package_namespace,
            package_type=infile_package.package_type,
            package_purl_appendix=infile_package.package_p_u_r_l_appendix,
            copyright=infile_package.copyright,
            license_name=infile_package.license_name,
            license_text=infile_package.license_text,
            url=infile_package.url,
            first_party=infile_package.first_party,
            exclude_from_notice=infile_package.exclude_from_notice,
            pre_selected=infile_package.pre_selected,
            follow_up=infile_package.follow_up,
            origin_id=infile_package.origin_id,
            origin_ids=infile_package.origin_ids,
            criticality=infile_package.criticality,
            was_preferred=infile_package.was_preferred,
        )

    @staticmethod
    def _convert_source(
        infile_source_info: opossum_file_package.SourceInfo,
    ) -> SourceInfo:
        return SourceInfo(
            name=infile_source_info.name,
            document_confidence=infile_source_info.document_confidence,
            additional_name=infile_source_info.additional_name,
        )
