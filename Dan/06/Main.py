"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

A_CMD = "A_COMMAND"
C_CMD = "C_COMMAND"
L_CMD = "L_COMMAND"

def init_labels(input_file: typing.TextIO, sym_table: SymbolTable) -> SymbolTable:
    """
    This function makes a first pass of the code a initializes all the labels in the code.
    Args:
        input_file (typing.TextIO): the file to assemble.
    
    Returns:
        Symbol_table: The updated table with all the symbols
    """
    index = 0
    parser = Parser(input_file)
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == L_CMD:
            symbol = parser.symbol()
            sym_table.add_entry(symbol,index)
        else:
            index += 1
    return sym_table

def init_variables(input_file: typing.TextIO, sym_table: SymbolTable) -> SymbolTable:
    """
    This function makes a second pass of the code a initializes all the variables in the code.
    Args:
        input_file (typing.TextIO): the file to assemble.
    
    Returns:
        Symbol_table: The updated table with all the symbols
    """
    # Next avaible ram index:
    n = 16
    parser = Parser(input_file)
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == A_CMD:
            symbol = parser.symbol()
            if not symbol.isdigit() and not sym_table.contains(symbol):
                sym_table.add_entry(symbol,n)
                n += 1
    return sym_table

def assemble_file(
        input_file: typing.TextIO, 
        output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")
    symbol_table = SymbolTable()
    symbol_table = init_labels(input_file, symbol_table)
    input_file.seek(0)
    symbol_table = init_variables(input_file,symbol_table)
    input_file.seek(0)
    parser = Parser(input_file=input_file)
    code = Code()

    while parser.has_more_commands():
        parser.advance()
        # Handle C command
        if parser.command_type() == C_CMD:
            # Get the command strings
            comp = parser.comp()
            dest = parser.dest()
            jump = parser.jump()
            # Translate the parts of the command to binary 
            comp_code = code.comp(comp)
            dest_code = code.dest(dest)
            jump_code = code.jump(jump)
            # Combine all the parts and write the c file to the command
            command = '1' + comp_code + dest_code + jump_code
            output_file.write(command + "\n")
        # Handle A command:
        elif parser.command_type() == A_CMD:
            symbol = parser.symbol()
            if symbol.isdigit():  # Numeric constant
                address_bin = format(int(symbol), "015b")
            else:
                address = symbol_table.get_address(symbol)
                address_bin = format(address, "015b")
            command = '0' + address_bin
            output_file.write(command + "\n")

if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
