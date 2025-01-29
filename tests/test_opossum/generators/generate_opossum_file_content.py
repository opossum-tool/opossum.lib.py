# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from faker.providers import BaseProvider

from opossum_lib.shared.entities.opossum_file_model import OpossumFileModel
from opossum_lib.shared.entities.opossum_input_file_model import OpossumInputFileModel
from opossum_lib.shared.entities.opossum_output_file_model import OpossumOutputFileModel
from tests.test_opossum.generators.generate_file_information import (
    FileInformationProvider,
)
from tests.test_opossum.generators.generate_outfile_information import (
    OpossumOutputFileProvider,
)


class OpossumFileContentProvider(BaseProvider):
    infile_provider: FileInformationProvider
    outfile_provider: OpossumOutputFileProvider

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.infile_provider = FileInformationProvider(generator)
        self.outfile_provider = OpossumOutputFileProvider(generator)

    def opossum_file_content(
        self,
        in_file: OpossumInputFileModel | None = None,
        out_file: OpossumOutputFileModel | None = None,
    ) -> OpossumFileModel:
        return OpossumFileModel(
            input_file=in_file or self.infile_provider.opossum_file_information(),
            output_file=out_file or self.outfile_provider.output_file(),
        )
