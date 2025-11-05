import re
from pathlib import Path

NOT_IMPORTANT = re.compile(
	r'/\*.*?\*/|//[^\n]*|[ \{\}\(\)]',
	re.S
)
PATH = Path(r'/Users/dan/Documents/Studies/Third Year/Semester A/Nand2Tetris/nand2tetris/projects/09/src')
JACK = '*.jack'

counter = 0
for file in PATH.glob(JACK):
	with file.open() as f:
		content = f.read()
	lines = NOT_IMPORTANT.sub('', content).splitlines()
	count = len(list(filter(None, lines)))
	print(f'{file.name}: {count}')
	counter += count

print(f'\nTOTAL: {counter}')
