"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


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
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        input_lines = input_file.read().splitlines()
        symbol_commands = []
        for command in input_lines:
            if not command or command.startswith("//"):
                continue
            if "//" in command:
                command = command.split("//")[0]
            command = command.replace(" ", "")
            symbol_commands.append(command)
        self.symbol_commands = symbol_commands
        self.input_lines = input_lines

        self.idx = 0
        self.l_commands = 1 if symbol_commands[0].startswith("(") else 0



    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.idx < len(self.symbol_commands)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """

        if self.command_type() == "L_COMMAND":
            self.l_commands += 1
        self.idx += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        current_command = self.symbol_commands[self.idx]
        if current_command.startswith("@"):
            return "A_COMMAND"
        if current_command.startswith("("):
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        current_command = self.symbol_commands[self.idx]
        if self.command_type() == "A_COMMAND":
            return current_command[1:]
        return current_command[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        current_command = self.symbol_commands[self.idx]
        eq_idx = current_command.find('=')
        if eq_idx == -1:
            return ""
        dest = current_command[:eq_idx]
        return dest.replace(" ", '')

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        current_command = self.symbol_commands[self.idx]
        eq_idx = current_command.find('=')
        semi_idx = current_command.find(';')

        if eq_idx == -1:
            res = current_command[:semi_idx] if semi_idx != -1 else current_command
        else:
            res = current_command[eq_idx + 1:semi_idx] if semi_idx != -1 else current_command[eq_idx + 1:]
        return res.replace(" ", '')
    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        current_command = self.symbol_commands[self.idx]
        if ';' not in current_command:
            return ''
        return current_command[current_command.find(';')+1:].replace(" ", '')

    def reset(self) -> None:
        self.idx = 0

