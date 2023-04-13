# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Dict

from spdx.model.document import CreationInfo
from spdx.model.file import File
from spdx.model.package import Package
from spdx.model.snippet import Snippet

from opossum_lib.opossum_file import OpossumPackage, SourceInfo


def create_package_attribution(package: Package) -> Dict[str, OpossumPackage]:
    package_attribution = dict()
    source = SourceInfo(package.spdx_id, 50)
    package_attribution[package.spdx_id] = OpossumPackage(
        source=source,
        packageName=package.name,
        url=str(package.download_location),
        packageVersion=package.version,
        copyright=str(package.copyright_text),
        comment=package.comment,
        licenseName=str(package.license_concluded),
    )

    return package_attribution


def create_file_attribution(file: File) -> Dict[str, OpossumPackage]:
    file_attributions = dict()
    source = SourceInfo(file.spdx_id, 50)
    file_attributions[file.spdx_id] = OpossumPackage(
        source=source,
        packageName=file.name.split("/")[-1],
        copyright=str(file.copyright_text),
        comment=file.comment,
        licenseName=str(file.license_concluded),
    )
    return file_attributions


def create_snippet_attribution(snippet: Snippet) -> Dict[str, OpossumPackage]:
    snippet_attributions = dict()

    source = SourceInfo(snippet.spdx_id, 50)
    snippet_attributions[snippet.spdx_id] = OpossumPackage(
        source=source,
        packageName=snippet.name,
        copyright=str(snippet.copyright_text),
        comment=snippet.comment,
        licenseName=str(snippet.license_concluded),
    )

    return snippet_attributions


def create_document_attribution(
    creation_info: CreationInfo,
) -> Dict[str, OpossumPackage]:
    document_attributions = dict()
    source = SourceInfo(creation_info.spdx_id, 50)
    document_attributions[creation_info.spdx_id] = OpossumPackage(
        source=source,
        packageName=creation_info.name,
        licenseName=creation_info.data_license,
    )

    return document_attributions
