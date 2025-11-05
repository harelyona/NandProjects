import glob
import os
import sys

COMPARE_EXTENSION = '.cmp'

from JackAnalyzer import analyze_file


def run_files_in_folder(folder_path):
    assert os.path.isdir(folder_path)
    print("Testing folder:", os.path.basename(folder_path), end=' ')

    files_to_assemble = [
        os.path.join(folder_path, filename)
        for filename in os.listdir(folder_path)]

    counter = 0
    all_true = True

    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".jack":
            continue
        counter += 1

        output_path = filename + ".xml"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            try:
                analyze_file(input_file, output_file)
            except:
                print("\n!!! Error while analyzing file:", input_path)
                raise
        this_true = compare_files(output_path, output_path + COMPARE_EXTENSION)
        all_true = all_true and this_true

    print(f"{counter} files found: Comparison is {all_true}")


def compare_files(our_path, compare_path):
    if open(our_path, 'r').read() != open(compare_path, 'r').read():
        print("\nDifference in file:", our_path)
        return False
    return True


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 3:
        print(len(sys.argv))
        sys.exit("Invalid usage, please use: run_tests <d|f> <input path>")
    assert sys.argv[1] in ['d', 'f']

    argument_path = os.path.abspath(sys.argv[2])
    assert os.path.isdir(argument_path)

    if sys.argv[1] == 'f':
        run_files_in_folder(argument_path)
    else:
        for dirpath in glob.glob(os.path.join(argument_path, '*')):
            if os.path.isdir(dirpath) and os.path.basename(dirpath)[0] not in ['.', '_']:
                run_files_in_folder(dirpath)
