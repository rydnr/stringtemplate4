#!/usr/bin/env python3
"""
 [The "BSD license"]
  Copyright (c) 2011 Terence Parr
  All rights reserved.

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions
  are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  3. The name of the author may not be used to endorse or promote products
     derived from this software without specific prior written permission.

  THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
  IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from enum import Enum
from typing import List, Optional, Tuple, Union, Dict

MAX_OPNDS: int = 2
OPND_SIZE_IN_BYTES: int = 2


class OperandType(Enum):
    NONE = 0
    STRING = 1
    ADDR = 2
    INT = 3


class Bytecode:

    class Instruction:
        def __init__(
            self,
            name: str,
            a: Optional["Bytecode.OperandType"] = None,
            b: Optional["Bytecode.OperandType"] = None,
        ):
            self.name: str = name  # E.g., "load_str", "new"
            self.type: List["Bytecode.OperandType"] = [OperandType.NONE] * MAX_OPNDS
            self.nopnds: int = 0

            if a is not None:
                self.type[0] = a
                self.nopnds = 1
                if b is not None:
                    self.type[1] = b
                    self.nopnds = 2

    # INSTRUCTION BYTECODES (byte is signed; use a short to keep 0..255)
    INSTR_LOAD_STR: int = 1
    INSTR_LOAD_ATTR: int = 2
    INSTR_LOAD_LOCAL: int = 3  # load stuff like it, i, i0
    INSTR_LOAD_PROP: int = 4
    INSTR_LOAD_PROP_IND: int = 5
    INSTR_STORE_OPTION: int = 6
    INSTR_STORE_ARG: int = 7
    INSTR_NEW: int = 8  # create new template instance
    INSTR_NEW_IND: int = 9  # create new instance using value on stack
    INSTR_NEW_BOX_ARGS: int = 10  # create new instance using args in Map on stack
    INSTR_SUPER_NEW: int = 11  # create new instance using value on stack
    INSTR_SUPER_NEW_BOX_ARGS: int = 12  # create new instance using args in Map on stack
    INSTR_WRITE: int = 13
    INSTR_WRITE_OPT: int = 14
    INSTR_MAP: int = 15  # <a:b()>, <a:b():c()>, <a:{...}>
    INSTR_ROT_MAP: int = 16  # <a:b(),c()>
    INSTR_ZIP_MAP: int = 17  # <names,phones:{n,p | ...}>
    INSTR_BR: int = 18
    INSTR_BRF: int = 19
    INSTR_OPTIONS: int = 20  # push options map
    INSTR_ARGS: int = 21  # push args map
    INSTR_PASSTHRU: int = 22
    # INSTR_PASSTHRU_IND: int = 23
    INSTR_LIST: int = 24
    INSTR_ADD: int = 25
    INSTR_TOSTR: int = 26

    # Predefined functions
    INSTR_FIRST: int = 27
    INSTR_LAST: int = 28
    INSTR_REST: int = 29
    INSTR_TRUNC: int = 30
    INSTR_STRIP: int = 31
    INSTR_TRIM: int = 32
    INSTR_LENGTH: int = 33
    INSTR_STRLEN: int = 34
    INSTR_REVERSE: int = 35

    INSTR_NOT: int = 36
    INSTR_OR: int = 37
    INSTR_AND: int = 38

    INSTR_INDENT: int = 39
    INSTR_DEDENT: int = 40
    INSTR_NEWLINE: int = 41

    INSTR_NOOP: int = 42  # do nothing
    INSTR_POP: int = 43
    INSTR_NULL: int = 44  # push null value
    INSTR_TRUE: int = 45  # push true value
    INSTR_FALSE: int = 46

    # combined instructions

    INSTR_WRITE_STR: int = 47  # load_str n, write
    INSTR_WRITE_LOCAL: int = 48  # TODO load_local n, write

    MAX_BYTECODE: int = 48

    # Used for assembly/disassembly; describes instruction set
    instructions: List[Optional["Bytecode.Instruction"]] = [
        None,  # <INVALID>
        Instruction("load_str", OperandType.STRING),  # index is the opcode
        Instruction("load_attr", OperandType.STRING),
        Instruction("load_local", OperandType.INT),
        Instruction("load_prop", OperandType.STRING),
        Instruction("load_prop_ind"),
        Instruction("store_option", OperandType.INT),
        Instruction("store_arg", OperandType.STRING),
        Instruction("new", OperandType.STRING, OperandType.INT),
        Instruction("new_ind", OperandType.INT),
        Instruction("new_box_args", OperandType.STRING),
        Instruction("super_new", OperandType.STRING, OperandType.INT),
        Instruction("super_new_box_args", OperandType.STRING),
        Instruction("write"),
        Instruction("write_opt"),
        Instruction("map"),
        Instruction("rot_map", OperandType.INT),
        Instruction("zip_map", OperandType.INT),
        Instruction("br", OperandType.ADDR),
        Instruction("brf", OperandType.ADDR),
        Instruction("options"),
        Instruction("args"),
        Instruction("passthru", OperandType.STRING),
        None,  # new Instruction("passthru_ind", OperandType.INT),
        Instruction("list"),
        Instruction("add"),
        Instruction("tostr"),
        Instruction("first"),
        Instruction("last"),
        Instruction("rest"),
        Instruction("trunc"),
        Instruction("strip"),
        Instruction("trim"),
        Instruction("length"),
        Instruction("strlen"),
        Instruction("reverse"),
        Instruction("not"),
        Instruction("or"),
        Instruction("and"),
        Instruction("indent", OperandType.STRING),
        Instruction("dedent"),
        Instruction("newline"),
        Instruction("noop"),
        Instruction("pop"),
        Instruction("null"),
        Instruction("true"),
        Instruction("false"),
        Instruction("write_str", OperandType.STRING),
        Instruction("write_local", OperandType.INT),
    ]


"""
Key changes and explanations:

    Enum for OperandType: The OperandType enum is defined using Python's enum.Enum class. This is a good way to represent a fixed set of named constants.
    Instruction Class: The Instruction class is defined to store the name and operand types of each instruction. The constructor handles the different numbers of operands using optional parameters and None as the default value.
    Instruction Constants: The bytecode instruction constants (INSTR_...) are defined as class-level variables with integer values.
    instructions List: The instructions list is created to hold Instruction objects, corresponding to the Java array. None is used as a placeholder for invalid or unused opcodes.
    Type Hints: Type hints are used for class variables, method parameters, and return values.
    Class-Level Variables: Class variables are used instead of static fields.

This Python code accurately defines the bytecode structure used by StringTemplate, including the operand types, instruction definitions, and the instruction set table.  This is a necessary foundation for implementing the StringTemplate compiler and interpreter. This class is crucial for the low-level operation of StringTemplate.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
