"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

A_CMD = "A_COMMAND"
C_CMD = "C_COMMAND"
L_CMD = "L_COMMAND"

class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Read all lines, strip whitespace, and remove comments
        self.lines = [
            line.split("//")[0].strip()
            for line in input_file.readlines()
            if line.strip() and not line.startswith("//")
        ]
        self.current_command = None
        self.current_index = -1
        

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.current_index < len(self.lines) - 1

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.current_index += 1
            self.current_command = self.lines[self.current_index]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.current_command.startswith("@"):
            return A_CMD
        elif self.current_command.startswith("(") and self.current_command.endswith(")"):
            return L_CMD
        else:
            return C_CMD



    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == A_CMD:
            return self.current_command[1:]  # Strip '@'
        elif self.command_type() == L_CMD:
            return self.current_command[1:-1]  # Strip '(' and ')'
        else:
            raise ValueError("symbol() called on a C_COMMAND.")

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == C_CMD:
            return self.current_command.split("=")[0] if "=" in self.current_command else ''
        else:
            raise ValueError("dest() called on a non-C_COMMAND.")

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == C_CMD:
            parts = self.current_command.split("=")
            comp = parts[1] if '=' in self.current_command else parts[0]
            return comp.split(';')[0]
        else:
            raise ValueError("comp() called on a non-C_COMMAND.")


    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == C_CMD:
            return self.current_command.split(";")[1] if ";" in self.current_command else ''
        else:
            raise ValueError("jump() called on a non-C_COMMAND.")