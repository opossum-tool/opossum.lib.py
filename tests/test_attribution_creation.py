# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

from license_expression import get_spdx_licensing
from spdx_tools.spdx.constants import DOCUMENT_SPDX_ID
from spdx_tools.spdx.model.actor import Actor, ActorType
from spdx_tools.spdx.model.checksum import Checksum, ChecksumAlgorithm
from spdx_tools.spdx.model.document import CreationInfo
from spdx_tools.spdx.model.file import File as SpdxFile
from spdx_tools.spdx.model.package import Package as SpdxPackage
from spdx_tools.spdx.model.snippet import Snippet as SpdxSnippet
from spdx_tools.spdx.model.spdx_no_assertion import SpdxNoAssertion

from opossum_lib.attribution_generation import (
    create_document_attribution,
    create_file_attribution,
    create_package_attribution,
    create_snippet_attribution,
)
from opossum_lib.opossum_file import OpossumPackage, SourceInfo


def test_create_package_attribution() -> None:
    package = SpdxPackage(
        name="Test Package",
        spdx_id="SPDXRef-Package",
        download_location="https://download.com",
        version="2.1.0",
        license_concluded=get_spdx_licensing().parse("MIT AND LGPL-2.0"),
        comment="Package comment",
        copyright_text=SpdxNoAssertion(),
    )
    package_attribution = create_package_attribution(package)

    assert package_attribution == OpossumPackage(
        source=SourceInfo(package.spdx_id),
        comment=package.comment,
        packageName=package.name,
        packageVersion=package.version,
        copyright=str(package.copyright_text),
        url=str(package.download_location),
        licenseName=str(package.license_concluded),
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
    file_attribution = create_file_attribution(file)

    assert file_attribution == OpossumPackage(
        source=SourceInfo(file.spdx_id),
        comment=file.comment,
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
    snippet_attribution = create_snippet_attribution(snippet)

    assert snippet_attribution == OpossumPackage(
        source=SourceInfo(snippet.spdx_id),
        comment=snippet.comment,
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
        created=datetime.utcnow(),
    )
    document_attribution = create_document_attribution(creation_info)

    assert document_attribution == OpossumPackage(
        source=SourceInfo(DOCUMENT_SPDX_ID),
        packageName=creation_info.name,
        licenseName=creation_info.data_license,
    )
