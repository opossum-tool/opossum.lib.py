# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from spdx_tools.spdx.model.document import CreationInfo
from spdx_tools.spdx.model.file import File
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.model.snippet import Snippet

from opossum_lib.constants import PURL
from opossum_lib.opossum_file import OpossumPackage, SourceInfo


def _get_purl(package: Package) -> Optional[str]:
    for external_reference in package.external_references:
        if external_reference.reference_type == PURL:
            return external_reference.locator
    return None


def create_package_attribution(package: Package) -> OpossumPackage:
    source = SourceInfo("SPDX-Package")
    package_attribution = OpossumPackage(
        source=source,
        packageName=package.name,
        url=str(package.download_location),
        packageVersion=package.version,
        packagePURLAppendix=_get_purl(package),
        copyright=str(package.copyright_text),
        comment=package.comment,
        licenseName=str(package.license_concluded),
    )

    return package_attribution


def create_file_attribution(file: File) -> OpossumPackage:
    source = SourceInfo("SPDX-File")
    file_attribution = OpossumPackage(
        source=source,
        packageName=file.name.split("/")[-1],
        copyright=str(file.copyright_text),
        comment=file.comment,
        licenseName=str(file.license_concluded),
    )
    return file_attribution


def create_snippet_attribution(snippet: Snippet) -> OpossumPackage:
    source = SourceInfo("SPDX-Snippet")
    snippet_attribution = OpossumPackage(
        source=source,
        packageName=snippet.name,
        copyright=str(snippet.copyright_text),
        comment=snippet.comment,
        licenseName=str(snippet.license_concluded),
    )

    return snippet_attribution


def create_document_attribution(
    creation_info: CreationInfo,
) -> OpossumPackage:
    source = SourceInfo(creation_info.spdx_id)
    document_attribution = OpossumPackage(
        source=source,
        packageName=creation_info.name,
        licenseName=creation_info.data_license,
    )

    return document_attribution
