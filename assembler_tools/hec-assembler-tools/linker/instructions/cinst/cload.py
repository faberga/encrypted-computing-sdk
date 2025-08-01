# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""@brief This module implements the cload C-instruction which loads data from SPAD to registers."""

from .cinstruction import CInstruction


class Instruction(CInstruction):
    """
    @brief Encapsulates a `cload` CInstruction.

    This instruction loads a single polynomial residue from scratchpad into a register.

    For more information, check the `cload` Specification:
        https://github.com/IntelLabs/hec-assembler-tools/blob/master/docsrc/inst_spec/cinst/cinst_cload.md
    """

    @classmethod
    def _get_num_tokens(cls) -> int:
        """
        @brief Gets the number of tokens required for the instruction.

        The `cload` instruction requires 4 tokens:
        <line: uint>, cload, <dst: str>, <src: uint>

        @return The number of tokens, which is 4.
        """
        # 4 tokens:
        # <line: uint>, cload, <dst: str>, <src: uint>
        # No HBM variant
        # <line: uint>, cload, <dst: str>, <src_var_name: str>
        return 4

    @classmethod
    def _get_name(cls) -> str:
        """
        @brief Gets the name of the instruction.

        @return The name of the instruction, which is "cload".
        """
        return "cload"

    def __init__(self, tokens: list, comment: str = ""):
        """
        @brief Constructs a new `cload` CInstruction.

        @param tokens A list of tokens representing the instruction.
        @param comment An optional comment for the instruction.
        @throws ValueError If the number of tokens is invalid or the instruction name is incorrect.
        """
        super().__init__(tokens, comment=comment)

    @property
    def source(self) -> str:
        """
        @brief Name of the source.
        This is a Variable name when loaded. Should be set to HBM address to write back.
        """
        return self.tokens[3]

    @source.setter
    def source(self, value: str):
        self.tokens[3] = value
