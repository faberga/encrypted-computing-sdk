# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import warnings

from argparse import Namespace

from .xinstruction import XInstruction
from assembler.memory_model.variable import Variable


class Instruction(XInstruction):
    """
    Encapsulates a `move` instruction when used to copy
    a variable into another variable through registers.
    """

    # To be initialized from ASM ISA spec
    _OP_NUM_TOKENS: int

    @classmethod
    def isa_spec_as_dict(cls) -> dict:
        """
        Returns isa_spec attributes as dictionary.
        """
        dict = super().isa_spec_as_dict()
        dict.update({"num_tokens": cls._OP_NUM_TOKENS})
        return dict

    @classmethod
    def SetNumTokens(cls, val):
        cls._OP_NUM_TOKENS = val

    @classmethod
    def _get_name(cls) -> str:
        """
        Returns the operation name in PISA format.

        Returns:
            str: PISA operation name.
        """
        return cls.op_name_pisa

    @classmethod
    def _get_op_name_pisa(cls) -> str:
        """
        Returns the operation name in PISA format.

        Returns:
            str: PISA operation name.
        """
        return "copy"

    @classmethod
    def _get_op_name_asm(cls) -> str:
        """
        Returns the operation name in ASM format.

        Returns:
            str: ASM operation name.
        """
        return "move"

    @classmethod
    def parseFromPISALine(cls, line: str) -> list:
        """
        Parses a `copy` instruction from a P-ISA Kernel instruction string.

        Parameters:
            line (str): String containing the instruction to parse.
                Instruction format: N, copy, dst (bank), src (bank), res=0 # comment
                Comment is optional.

                Example line:
                "13, copy, output_0_1_3 (2), c_0_1_3 (0), 0"

        Returns:
            Namespace: A namespace with the following attributes:
                N (int): Ring size = Log_2(PMD)
                op_name (str): Operation name ("copy")
                dst (list[(str, int)]): List of destinations of the form (variable_name, suggested_bank).
                    This list has a single element for `copy`.
                src (list[(str, int)]): List of sources of the form (variable_name, suggested_bank).
                    This list has two elements for `copy`.
                res: Residual for the operation. Ignored for copy/move
                comment (str): String with the comment attached to the line (empty string if no comment).
        """
        retval = None
        tokens = XInstruction.tokenizeFromPISALine(cls.op_name_pisa, line)
        if tokens:
            retval = {"comment": tokens[1]}
            instr_tokens = tokens[0]
            if len(instr_tokens) > cls._OP_NUM_TOKENS:
                warnings.warn(
                    f'Extra tokens detected for instruction "{cls.op_name_pisa}"',
                    SyntaxWarning,
                )

            retval["N"] = int(instr_tokens[0])
            retval["op_name"] = instr_tokens[1]
            params_start = 2
            params_end = params_start + cls._OP_NUM_DESTS + cls._OP_NUM_SOURCES
            dst_src = cls.parsePISASourceDestsFromTokens(
                instr_tokens, cls._OP_NUM_DESTS, cls._OP_NUM_SOURCES, params_start
            )
            retval.update(dst_src)
            if len(instr_tokens) < cls._OP_NUM_TOKENS:
                # temporary warning to avoid syntax error during testing
                # REMOVE WARNING AND TURN IT TO ERROR DURING PRODUCTION
                # ---------------------------
                warnings.warn(
                    f'Not enough tokens detected for instruction "{cls.op_name_pisa}"',
                    SyntaxWarning,
                )
                pass
            else:
                # ignore "res", but make sure it exists (syntax)
                assert instr_tokens[params_end] is not None

            retval = Namespace(**retval)
            assert retval.op_name == cls.op_name_pisa
        return retval

    def __init__(
        self,
        id: int,
        N: int,
        dst: list,
        src: list,
        throughput: int = None,
        latency: int = None,
        comment: str = "",
    ):
        """
        Initializes an Instruction object with the given parameters.

        Parameters:
            id (int): The unique identifier for the instruction.
            N (int): The ring size, typically Log_2(PMD).
            dst (list): List of destination variables.
            src (list): List of source variables.
            throughput (int, optional): The throughput of the instruction. Defaults to None.
            latency (int, optional): The latency of the instruction. Defaults to None.
            comment (str, optional): A comment associated with the instruction. Defaults to an empty string.

        Raises:
            ValueError: If the source and destination are the same.
        """
        if not throughput:
            throughput = Instruction._OP_DEFAULT_THROUGHPUT
        if not latency:
            latency = Instruction._OP_DEFAULT_LATENCY
        N = 0  # does not require ring-size
        super().__init__(id, N, throughput, latency, comment=comment)
        if dst[0].name == src[0].name:
            raise ValueError(
                f'`dst`: Source and destination cannot be the same for instruction "{self.name}".'
            )
        self._set_dests(dst)
        self._set_sources(src)

    def __repr__(self):
        """
        Returns a string representation of the Instruction object.

        Returns:
            str: A string representation of object.
        """
        retval = (
            "<{}({}) object at {}>(id={}[0], "
            "dst={}, src={}, "
            "throughput={}, latency={})"
        ).format(
            type(self).__name__,
            self.name,
            hex(id(self)),
            self.id,
            self.dests,
            self.sources,
            self.throughput,
            self.latency,
        )
        return retval

    def _set_dests(self, value):
        """
        Sets the destination variables for the instruction.

        Parameters:
            value (list): List of destination variables.

        Raises:
            ValueError: If the list does not contain the expected number of `Variable` objects.
        """
        if len(value) != Instruction._OP_NUM_DESTS:
            raise ValueError(
                (
                    "`value`: Expected list of {} `Variable` objects, "
                    "but list with {} elements received.".format(
                        Instruction._OP_NUM_SOURCES, len(value)
                    )
                )
            )
        if not all(isinstance(x, Variable) for x in value):
            raise ValueError("`value`: Expected list of `Variable` objects.")
        super()._set_dests(value)

    def _set_sources(self, value):
        """
        Sets the source variables for the instruction.

        Parameters:
            value (list): List of source variables.

        Raises:
            ValueError: If the list does not contain the expected number of `Variable` objects.
        """
        if len(value) != Instruction._OP_NUM_SOURCES:
            raise ValueError(
                (
                    "`value`: Expected list of {} `Variable` objects, "
                    "but list with {} elements received.".format(
                        Instruction._OP_NUM_SOURCES, len(value)
                    )
                )
            )
        if not all(isinstance(x, Variable) for x in value):
            raise ValueError("`value`: Expected list of `Variable` objects.")
        super()._set_sources(value)

    def _to_pisa_format(self, *extra_args) -> str:
        """
        Converts the instruction to P-ISA kernel format.

        Parameters:
            *extra_args: Additional arguments (not supported).

        Raises:
            ValueError: If extra arguments are provided.

        Returns:
            str: P-ISA kernel format instruction.
        """
        assert len(self.dests) == Instruction._OP_NUM_DESTS
        assert len(self.sources) == Instruction._OP_NUM_SOURCES

        if extra_args:
            raise ValueError("`extra_args` not supported.")

        return super()._to_pisa_format()

    def _to_xasmisa_format(self, *extra_args) -> str:
        """
        Converts the instruction to ASM format.

        Parameters:
            *extra_args: Additional arguments (not supported).

        Raises:
            ValueError: If extra arguments are provided.

        Returns:
            str: ASM format instruction.
        """
        assert len(self.dests) == Instruction._OP_NUM_DESTS
        assert len(self.sources) == Instruction._OP_NUM_SOURCES

        if extra_args:
            raise ValueError("`extra_args` not supported.")

        return super()._to_xasmisa_format()
