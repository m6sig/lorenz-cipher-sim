A fork of https://github.com/RealGrep/lorenz-cipher-sim

Now works on Python3 with better command line interface.
Reduced numbers of LTRS/FIGS symbol to rise the bar for chosen plaintext attack to the same level as the real machine. 
Improve wheel generation speed.
Randomise wheel indicator numbers.

Usage:
$ python3 lorenz-sz40.py [-h] [--keygen <key file>]
                         [--encrypt <input file> <key file> <output file>]
                         [--decrypt <input file> <key file> <output file>]
                         [--readtape <input file>]

optional arguments:
  -h, --help            show this help message and exit
  --keygen <key file>   Creates a random key file with normal SZ40 teeth
                        counts and sets random indicators. Edit the file to
                        suit.
  --encrypt <input file> <key file> <output file>
                        Encode ASCII plaintext to Baudot code (5 bits per
                        byte) and encrypt with wheel settings in key file,
                        writing ciphertext to output file.
  --decrypt <input file> <key file> <output file>
                        Decrypt the input file with wheel settings in key
                        file, decode from Baudot code and and output ASCII
                        plaintext to output file.
  --readtape <input file>
                        Read input file in Baudot code and display ASCII
                        equivalent.

Example:
  python3 lorenz.py --keygen <key file>
  python3 lorenz.py --encrypt <input file> <key file> <output file>
  python3 lorenz.py --decrypt <input file> <key file> <output file>
  python3 lorenz.py --readtape <input file>
