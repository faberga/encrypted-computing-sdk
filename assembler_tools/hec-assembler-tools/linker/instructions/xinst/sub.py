# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""@brief This module implements the sub X-instruction which performs element-wise polynomial subtraction."""

from .xinstruction import XInstruction


class Instruction(XInstruction):
    """
    @brief Encapsulates a `sub` XInstruction.

    This instruction performs element-wise polynomial subtraction.

    For more information, check the specification:
        https://github.com/IntelLabs/hec-assembler-tools/blob/master/docsrc/inst_spec/xinst/xinst_sub.md
    """

    @classmethod
    def _get_num_tokens(cls) -> int:
        """
        @brief Gets the number of tokens required for the instruction.

        The `sub` instruction requires 7 tokens:
        F<bundle_idx: uint>, <info: str>, sub, <dst: str>, <src0: str>, <src1: str>, <res: uint>

        @return The number of tokens, which is 7.
        """
        return 7

    @classmethod
    def _get_name(cls) -> str:
        """
        @brief Gets the name of the instruction.

        @return The name of the instruction, which is "sub".
        """
        return "sub"

    def __init__(self, tokens: list, comment: str = ""):
        """
        @brief Constructs a new `sub` XInstruction.

        @param tokens A list of tokens representing the instruction.
        @param comment An optional comment for the instruction.
        @throws ValueError If the number of tokens is invalid or the instruction name is incorrect.
        """
        super().__init__(tokens, comment=comment)
