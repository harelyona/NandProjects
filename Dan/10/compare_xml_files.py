import os

def compare_files(file1, file2):
    """Compare two files ignoring leading whitespace differences."""
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            lines1 = [line.lstrip() for line in f1.readlines()]
            lines2 = [line.lstrip() for line in f2.readlines()]
            return lines1 == lines2
    except FileNotFoundError:
        return False

def find_and_compare_files(root_dir):
    """Recursively compare XML files (filename.xml and filename_my.xml) in subdirectories."""
    matches = []
    differences = []

    for subdir, _, files in os.walk(root_dir):
        xml_files = [f for f in files if f.endswith('.xml')]
        for file in xml_files:
            if not file.endswith('_my.xml'):
                base_name = os.path.splitext(file)[0]
                file1 = os.path.join(subdir, file)
                file2 = os.path.join(subdir, f"{base_name}_my.xml")

                if os.path.exists(file2):
                    if compare_files(file1, file2):
                        matches.append((file1, file2))
                    else:
                        differences.append((file1, file2))

    return matches, differences

if __name__ == "__main__":
    root_directory = input("Enter the root directory path: ").strip()
    if not os.path.isdir(root_directory):
        print("Invalid directory path. Please try again.")
        exit(1)

    matches, differences = find_and_compare_files(root_directory)

    print("\nMatching files:")
    for file1, file2 in matches:
        print(f"  {file1} == {file2}")

    print("\nDifferent files:")
    for file1, file2 in differences:
        print(f"  {file1} != {file2}")
