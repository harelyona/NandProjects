"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

# Constants:
INV_ADV = "The file doesn't have any more lines to advance to."
INV_CMD = "No current command. Call advance() first."

class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line's end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    command_types: typing.Dict[str,str] = {
        'add': "C_ARITHMETIC",
        'sub': "C_ARITHMETIC",
        'and': "C_ARITHMETIC",
        'or': "C_ARITHMETIC",
        'eq': "C_ARITHMETIC",
        'gt': "C_ARITHMETIC",
        'lt': "C_ARITHMETIC",
        'neg': "C_ARITHMETIC",
        'not': "C_ARITHMETIC",
        'shiftleft': "C_ARITHMETIC",
        'shiftright': "C_ARITHMETIC",
        'push': "C_PUSH",
        'pop': "C_POP",
        'label': "C_LABEL",
        'goto': "C_GOTO",
        'if-goto': "C_IF",
        'function': "C_FUNCTION",
        'return': "C_RETURN",
        'call': "C_CALL"
    }

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Strip all the lines from comments and and blank lines:
        self.lines = []
        for line in input_file.readlines():
            line = line.split('//')[0].strip()
            # If line is not empty than append to lines list:
            if line:
                self.lines.append(line)

        self.current_line = -1
        self.current_command = None

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.current_line < len(self.lines) - 1


    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.current_line += 1
            self.current_command = self.lines[self.current_line]
        else:
            raise ValueError(INV_ADV)

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if self.current_command is None:
            raise ValueError(INV_CMD)
    
        first_word = self.current_command.split()[0]
        command_type = self.command_types.get(first_word)
        
        if command_type is None:
            raise ValueError(f"Unrecognized command: {first_word}")
        
        return command_type

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.current_command is None:
            raise ValueError(INV_CMD)
        
        if self.command_type() == "C_ARITHMETIC":
            first_word = self.current_command.split()[0]
            return first_word
        
        if self.command_type() == "C_RETURN":
            raise ValueError("Cannot call arg1 for 'C_RETURN' commands.")
        
        return self.current_command.split()[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        if self.current_command is None:
            raise ValueError(INV_CMD)
        
        valid_commands = ['C_PUSH','C_POP','C_FUNCTION','C_CALL']

        if self.command_type() not in valid_commands:
            raise ValueError(f"The method arg2 can't be called on the command {self.command_type()}.")

        parts = self.current_command.split()
        if len(parts) < 3:
            raise ValueError(f"Command {self.current_command} does not have a second argument.")
    
        try:
            return int(parts[2])
        except ValueError:
            raise ValueError(f"Expected an integer for the second argument in {self.current_command}.")

