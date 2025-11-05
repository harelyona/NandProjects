# Script to convert words in a text file to a specific format

def convert_words(input_file, output_file):
    try:
        # Open the input file for reading
        with open(input_file, 'r') as infile:
            # Read all lines and strip any extra whitespace
            words = [line.strip() for line in infile if line.strip()]

        # Open the output file for writing
        with open(output_file, 'w') as outfile:
            # Write each word in the desired format
            for i, word in enumerate(words):
                outfile.write(f'let list[{i}] = "{word.upper()}";\n')


        print(f"Conversion complete. Output written to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {input_file} does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
# Replace 'input.txt' and 'output.txt' with the paths to your files
input_file = '/Users/dan/Documents/Studies/Third Year/Semester A/Nand2Tetris/nand2tetris/projects/09/words.txt'
output_file = '/Users/dan/Documents/Studies/Third Year/Semester A/Nand2Tetris/nand2tetris/projects/09/output.txt'
convert_words(input_file, output_file)
