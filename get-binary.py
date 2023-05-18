from sys import argv

with open(argv[1], "rb") as f:
	open("bin.temp", 'w').write(repr(f.read()))