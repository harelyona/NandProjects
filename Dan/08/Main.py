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
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO,
        bootstrap: bool) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
        bootstrap (bool): if this is True, the current file is the 
            first file we are translating.
    """
    parser = Parser(input_file)
    code_writer = CodeWriter(output_file)

    # Set the filename for static usage in the codewriter object.
    input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    code_writer.set_file_name(input_filename)

    # Handle bootstrap
    if bootstrap:
        # Initialize the SP and call sys init.
        output_file.write("// Bootstrap the program:\n")
        output_file.write("@256\nD=A\n@SP\nM=D\n")
        code_writer.write_call("Sys.init", 0)

    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        if command_type == "C_ARITHMETIC":
            command = parser.arg1()
            code_writer.write_arithmetic(command)
        elif command_type == "C_POP":
            segment = parser.arg1()
            index = parser.arg2()
            code_writer.write_push_pop("C_POP", segment, index)
        elif command_type == "C_PUSH":
            segment = parser.arg1()
            index = parser.arg2()
            code_writer.write_push_pop("C_PUSH", segment, index)
        elif command_type == "C_LABEL":
            label = parser.arg1()
            code_writer.write_label(label)
        elif command_type == "C_GOTO":
            label = parser.arg1()
            code_writer.write_goto(label)
        elif command_type == "C_IF":
            label = parser.arg1()
            code_writer.write_if(label)
        elif command_type == "C_FUNCTION":
            func_name = parser.arg1()
            num_vars = parser.arg2()
            code_writer.write_function(func_name, num_vars)
        elif command_type == "C_RETURN":
            code_writer.write_return()
        elif command_type == "C_CALL":
            func_name = parser.arg1()
            num_args = parser.arg2()
            code_writer.write_call(func_name, num_args)

if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    a = r"C:\Users\harel\Desktop\Nand\NandProjects\08\ProgramFlow\BasicLoop\BasicLoop.vm"
    argument_path = os.path.abspath(a)
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)
            bootstrap = False
