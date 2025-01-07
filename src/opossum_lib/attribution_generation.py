# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from io import StringIO

from spdx_tools.spdx.model.document import CreationInfo
from spdx_tools.spdx.model.file import File
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.model.snippet import Snippet
from spdx_tools.spdx.writer.tagvalue.creation_info_writer import write_creation_info
from spdx_tools.spdx.writer.tagvalue.file_writer import write_file
from spdx_tools.spdx.writer.tagvalue.package_writer import write_package
from spdx_tools.spdx.writer.tagvalue.snippet_writer import write_snippet

from opossum_lib.constants import (
    PURL,
    SPDX_FILE_IDENTIFIER,
    SPDX_PACKAGE_IDENTIFIER,
    SPDX_SNIPPET_IDENTIFIER,
)
from opossum_lib.opossum_file import OpossumPackage, SourceInfo


def _get_purl(package: Package) -> str | None:
    for external_reference in package.external_references:
        if external_reference.reference_type == PURL:
            return external_reference.locator
    return None


def create_package_attribution(package: Package) -> OpossumPackage:
    package_data = StringIO()
    write_package(package, package_data)
    source = SourceInfo(SPDX_PACKAGE_IDENTIFIER)
    package_attribution = OpossumPackage(
        source=source,
        packageName=package.name,
        url=str(package.download_location),
        packageVersion=package.version,
        packagePURLAppendix=_get_purl(package),
        copyright=str(package.copyright_text),
        comment=package_data.getvalue(),
        licenseName=str(package.license_concluded),
    )

    return package_attribution


def create_file_attribution(file: File) -> OpossumPackage:
    file_data = StringIO()
    write_file(file, file_data)
    source = SourceInfo(SPDX_FILE_IDENTIFIER)
    file_attribution = OpossumPackage(
        source=source,
        packageName=file.name.split("/")[-1],
        copyright=str(file.copyright_text),
        comment=file_data.getvalue(),
        licenseName=str(file.license_concluded),
    )
    return file_attribution


def create_snippet_attribution(snippet: Snippet) -> OpossumPackage:
    snippet_data = StringIO()
    write_snippet(snippet, snippet_data)
    source = SourceInfo(SPDX_SNIPPET_IDENTIFIER)
    snippet_attribution = OpossumPackage(
        source=source,
        packageName=snippet.name,
        copyright=str(snippet.copyright_text),
        comment=snippet_data.getvalue(),
        licenseName=str(snippet.license_concluded),
    )

    return snippet_attribution


def create_document_attribution(
    creation_info: CreationInfo,
) -> OpossumPackage:
    creation_info_data = StringIO()
    write_creation_info(creation_info, creation_info_data)
    source = SourceInfo(creation_info.spdx_id)
    document_attribution = OpossumPackage(
        source=source,
        packageName=creation_info.name,
        licenseName=creation_info.data_license,
        comment=creation_info_data.getvalue(),
    )

    return document_attribution
