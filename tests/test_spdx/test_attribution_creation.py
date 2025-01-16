# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from datetime import UTC, datetime
from io import StringIO

from license_expression import get_spdx_licensing
from spdx_tools.spdx.constants import DOCUMENT_SPDX_ID
from spdx_tools.spdx.model.actor import Actor, ActorType
from spdx_tools.spdx.model.checksum import Checksum, ChecksumAlgorithm
from spdx_tools.spdx.model.document import CreationInfo
from spdx_tools.spdx.model.file import File as SpdxFile
from spdx_tools.spdx.model.package import ExternalPackageRef, ExternalPackageRefCategory
from spdx_tools.spdx.model.package import Package as SpdxPackage
from spdx_tools.spdx.model.snippet import Snippet as SpdxSnippet
from spdx_tools.spdx.model.spdx_no_assertion import SpdxNoAssertion
from spdx_tools.spdx.writer.tagvalue.creation_info_writer import write_creation_info
from spdx_tools.spdx.writer.tagvalue.file_writer import write_file
from spdx_tools.spdx.writer.tagvalue.package_writer import write_package
from spdx_tools.spdx.writer.tagvalue.snippet_writer import write_snippet

from opossum_lib.opossum.opossum_file import OpossumPackage, SourceInfo
from opossum_lib.spdx.attribution_generation import (
    create_document_attribution,
    create_file_attribution,
    create_package_attribution,
    create_snippet_attribution,
)
from opossum_lib.spdx.constants import (
    SPDX_FILE_IDENTIFIER,
    SPDX_PACKAGE_IDENTIFIER,
    SPDX_SNIPPET_IDENTIFIER,
)


def test_create_package_attribution() -> None:
    package = SpdxPackage(
        name="Test Package",
        spdx_id="SPDXRef-Package",
        download_location="https://download.com",
        version="2.1.0",
        license_concluded=get_spdx_licensing().parse("MIT AND LGPL-2.0"),
        comment="Package comment",
        copyright_text=SpdxNoAssertion(),
        external_references=[
            ExternalPackageRef(
                ExternalPackageRefCategory.PACKAGE_MANAGER,
                "purl",
                "pkg:maven/org.apache.jena/apache-jena@3.12.0",
            )
        ],
    )
    package_data = StringIO()
    write_package(package, package_data)
    package_attribution = create_package_attribution(package)

    assert package_attribution == OpossumPackage(
        source=SourceInfo(name=SPDX_PACKAGE_IDENTIFIER),
        comment=package_data.getvalue(),
        packageName=package.name,
        packageVersion=package.version,
        copyright=str(package.copyright_text),
        url=str(package.download_location),
        licenseName=str(package.license_concluded),
        packagePURLAppendix="pkg:maven/org.apache.jena/apache-jena@3.12.0",
    )


def test_create_file_attribution() -> None:
    file = SpdxFile(
        name="Test File",
        spdx_id="SPDXRef-File",
        checksums=[Checksum(ChecksumAlgorithm.SHA1, "")],
        license_concluded=get_spdx_licensing().parse("Apache-2.0 OR MIT"),
        comment="File comment",
        copyright_text="Copyright (c) 2023 someone",
    )
    file_data = StringIO()
    write_file(file, file_data)
    file_attribution = create_file_attribution(file)

    assert file_attribution == OpossumPackage(
        source=SourceInfo(name=SPDX_FILE_IDENTIFIER),
        comment=file_data.getvalue(),
        packageName=file.name,
        copyright=str(file.copyright_text),
        licenseName=str(file.license_concluded),
    )


def test_create_snippet_attribution() -> None:
    snippet = SpdxSnippet(
        name="Test Snippet",
        spdx_id="SPDXRef-Snippet",
        file_spdx_id="SPDXRef-File",
        byte_range=(1, 2),
        license_concluded=get_spdx_licensing().parse("MIT AND LGPL-2.0"),
        comment="Snippet comment",
        copyright_text=SpdxNoAssertion(),
    )
    snippet_data = StringIO()
    write_snippet(snippet, snippet_data)
    snippet_attribution = create_snippet_attribution(snippet)

    assert snippet_attribution == OpossumPackage(
        source=SourceInfo(name=SPDX_SNIPPET_IDENTIFIER),
        comment=snippet_data.getvalue(),
        packageName=snippet.name,
        licenseName=str(snippet.license_concluded),
        copyright=str(snippet.copyright_text),
    )


def test_create_document_attribution() -> None:
    creation_info = CreationInfo(
        name="Test Document",
        spdx_id=DOCUMENT_SPDX_ID,
        spdx_version="SPDX2.3",
        document_namespace="some.namespace",
        creators=[Actor(ActorType.PERSON, "Name")],
        created=datetime.now(UTC),
    )
    creation_info_data = StringIO()
    write_creation_info(creation_info, creation_info_data)
    document_attribution = create_document_attribution(creation_info)

    assert document_attribution == OpossumPackage(
        source=SourceInfo(name=DOCUMENT_SPDX_ID),
        packageName=creation_info.name,
        licenseName=creation_info.data_license,
        comment=creation_info_data.getvalue(),
    )
