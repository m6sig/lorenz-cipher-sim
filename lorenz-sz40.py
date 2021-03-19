#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2012, Mike Dusseault(RealGrep)
# Copyright 2020-2021, M6SIG

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Lorenz Sz40 Cipher Machine simulator
#

import sys
import textwrap
import argparse
from pathlib import Path
import random
randgen = random.SystemRandom()

'''ASCII/TTY coding conversion data.'''

# Constants for asc2tty array
INVC   = 255    # invalid character mapping
FIGS_F = 128    # figures required flag
ETHR_F = 64     # valid in either shift
LTRS   = 31     # letters shift character
FIGS   = 27     # figures shift character
MSK5   = 31     # mask off 5 LSBs
MSK7   = 127    # mask off 7 LSBs

# For converting ASCII to 5-bits TTY code.
#
# 5 LSBs are significant.
# Bit 7 set if figures shift required.
# 0xff indicates invalid character mapping.
# Lower-case mapped to upper-case
#
# Dollor  $  represents "WHO ARE YOU" 
# Tilda  (~) represents "Bell"
asc2tty = [ 
# NUL                                       \a
  64, INVC, INVC, INVC, INVC, INVC, INVC,  154, INVC, INVC,
# \n                \r
  72, INVC, INVC,   66, INVC, INVC, INVC, INVC, INVC, INVC,
INVC, INVC, INVC, INVC, INVC, INVC, INVC, INVC, INVC, INVC,
#             ' '    !     "     #     $     %     &     '
INVC, INVC,   68, INVC, INVC, INVC,  146, INVC, INVC,  148,
#  (     )     *     +     ,     -     .     /
 158,  137, INVC,  145,  134,  152,  135,  151,
# 0     1    2    3    4    5    6    7    8    9    :     
 141, 157, 153, 144, 138, 129, 149, 156, 140, 131, 142,
#  ;    <    =    >    ?    @   A   B   C   D   E   F   G
INVC, 158, 143, 137, 147,INVC, 24, 19, 14, 18, 16, 22, 11,
# H   I   J   K  L  M  N   O   P  Q   R   S  T   U   V   W
  5, 12, 26, 30, 9, 7, 6, 3, 13, 29, 10, 20, 1, 28, 15, 25,
# X   Y   Z    [     \    ]     ^     _     `   a   b   c
 23, 21, 17, 158, INVC, 137, INVC, INVC, INVC, 24, 19, 14,
# d   e   f   g  h   i   j   k  l  m  n   o  p   q   r   s
 18, 16, 22, 11, 5, 12, 26, 30, 9, 7, 6, 3, 13, 29, 10, 20,
# t   u   v   w   x   y   z    {     |    }    ~   DEL
  1, 28, 15, 25, 23, 21, 17, 158, INVC, 137, 154, INVC]

# For converting 5-bits TTY code to ASCII.
tty_ltrs2asc = [
    '\x00', 'T',         '\x0D',  'O', ' ', 'H', 'N', 'M',
    '\x0A', 'L',            'R',  'G', 'I', 'P', 'C', 'V',
       'E', 'Z',            'D',  'B', 'S', 'Y', 'F', 'X',
       'A', 'W',            'J', FIGS, 'U', 'Q', 'K', LTRS]

tty_figs2asc = [
    '\x00', '5',         '\x0D',  '9', ' ', '&', ',', '.',
    '\x0A', ')',            '4',  '&', '8', '0', ':', '=',
       '3', '+', 'Who Are You?',  '?', "'", '6', '&', '/',
       '-', '2',         '\x07', FIGS, '7', '1', '(', LTRS]

# Mike's convertion:
# From http://www.codesandciphers.org.uk/lorenz/fish.htm
#           0    1    2    3    4    5    6    7    8    9
# B2A_LTRS = ['*', 'E','\n', 'A', ' ', 'S', 'I', 'U','\r', 'D',
#           10   11  12    13   14   15   16   17   18   19
#            'R', 'J', 'N', 'F', 'C', 'K', 'T', 'Z', 'L', 'W',
#           20   21   22   23   24   25   26   27   28   29
#            'H', 'Y', 'P', 'Q', 'O', 'B', 'G',  '', 'M', 'X',
#           30   31
#            'V', '']
# Tilda (~) here represents "WHO ARE YOU" message. * is a nul.
#           0    1    2    3    4    5    6    7    8    9
# B2A_FIGS = ['*', '3','\n', '-', ' ','\'', '8', '7','\r', '~',
#           10   11   12   13   14   15   16   17   18   19
#            '4','\b', ',', '%', ':', '(', '5', '+', ')', '2',
#           20   21   22   23   24   25   26   27   28   29
#            '#', '6', '0', '1', '9', '?', '@',  '', '.', '/',
#           30   31
#            '=', '']


def ascii2tty(s):
    '''Convert from ASCII to 5-bits TTY code.

    Assumes reader may initially be in either letters or figures
    shift, and emits a shift char prior to first output char that
    is not valid in either shift.'''

    figs = False
    result = []
    # Emit initial shift if needed
    if len(s) > 0:
        char = asc2tty[s[0] & MSK7]
        if (char & ETHR_F):
            # Valid in either shift
            pass
        elif (char & FIGS_F):
            # Must be in figures shift
            result.append(chr(FIGS))
            figs = True
        else:
            # Must be in letters shift
            result.append(chr(LTRS))
            figs = False
    
    # Convert chars
    for char in s:
        # Drop MSB and convert
        char = asc2tty[char & MSK7]

        # Convert if valid
        if char != INVC:

            # Emit shift char if needed
            if (char & ETHR_F):
                # Valid in either shift
                pass
            elif (char & FIGS_F):
                # Must be in figures shift
                if figs is not True:
                    # Not already in figures shift
                    # i.e. either in letters shift or indeterminate
                    result.append(chr(FIGS))
                    figs = True
            elif figs is not False:
                # In figures or indeterminate shift, but must be in letter shift
                result.append(chr(LTRS))
                figs = False

            # Emit the converted char
            result.append(chr(char & MSK5))

    return ''.join(result)


def tty2ascii(s):
    '''Convert from 5-level TTY code to ASCII.

    Assumes initial letters shift state.'''

    figs = False
    result = []
    for char in s:
        char = ord(char) & MSK5
        if char == LTRS:
            figs = False
        elif char == FIGS:
            figs = True
        else:
            if figs:
                char = tty_figs2asc[char]
            else:
                char = tty_ltrs2asc[char]
            result.append(char)

    return ''.join(result)


class Wheel:
    """ Class representing a specific wheel. """

    def __init__(self, wheel_data, initial):
        self.wheel_data = wheel_data
        self.wheel_size = len(wheel_data)
        self.state = initial

    def advance(self):
        self.state = (self.state + 1) % self.wheel_size

    def get_val(self):
        return self.wheel_data[self.state]

    def get_current_pos(self):
        return self.state

    def __repr__(self):
        return "State:" + str(self.state) + "; Size:" +\
               str(self.wheel_size) + "; Wheel:" + str(self.wheel_data)


class WheelBank:
    """ Class for a bank of wheels. """

    def __init__(self, wheels):
        self.wheels = wheels

    def advance(self):
        for w in self.wheels:
            w.advance()

    def get_val(self):
        result = []
        for i in list(range(5)):
            result.append(self.wheels[i].get_val())
        # Wheel numbered 1 is low bit, so we need to flip the bit order.
        # NOTE: I'm not 100% sure which wheel has the MSB and which the
        # LSB. Would be nice to confirm this better. Diagrams seem to show
        # wheel K1, for example, on input 1. And a Baudot code chart nearby
        # shows bit #1 as LSB. So I think this is right...
        return int("0b" + ''.join([str(i) for i in result[::-1]]), 2)


    def __repr__(self):
        result = []
        for e in self.wheels:
            result.append(str(e))
        return '\n'.join(result)


class MotorWheelBank(WheelBank):
    """ Class for the motor wheel bank, which is slightly different than
        the other wheel banks. Inherits from WheelBank, but overrides the
        advance() method and adds an is_active() method to see if the S
        wheels should be advanced.
    """

    def advance(self):
        self.wheels[0].advance()
        if self.wheels[0].get_val():
            self.wheels[1].advance()


    def is_active(self):
        return self.wheels[1].get_val()


class LorenzCipher:
    """ Represents an instance of a Lorenz Cipher Machine. """

    def __init__(self, K, S, M, initial=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]):
        self.K_wheels = WheelBank([Wheel(data, i)
                                   for data, i in zip(K, initial[:5])])
        self.S_wheels = WheelBank([Wheel(data, i)
                                   for data, i in zip(S, initial[7:])])
        self.M_wheels = MotorWheelBank([Wheel(data, i)
                                        for data, i in zip(M, initial[5:8])])

    def advance(self):
        """ Advances the wheels. Should be called after every encrypt or
            decrypt.
        """
        # K wheels advance every time
        self.K_wheels.advance()

        # M wheels "advance" every time. They do not all advance, like
        # K and S wheels. See MotorWheelBank class for details.
        self.M_wheels.advance()

        # If the M_wheels are set such that the S wheels should advance,
        # do so.
        if self.M_wheels.is_active():
            self.S_wheels.advance()

    def crypt_char(self, c):
        """ Encrypt/decrypt a single character. Expects an ordinal of the
            character.
        """

        result = c ^ self.K_wheels.get_val() ^ self.S_wheels.get_val()
        self.advance()
        return result

    def crypt(self, m):
        """ Encrypt/decrypt a message string. Uses Baudot encoding. """

        return ''.join([chr(self.crypt_char(ord(c))) for c in m])


def write_keyfile(output_file, K_sizes, S_sizes, M_sizes,
                  K_wheels, S_wheels, M_wheels, indicator):
    with open(output_file, 'w') as f_out:
        f_out.write("# Number of teeth on each wheel [K1, K2, K3, K4, K5]\n")
        f_out.write("K_sizes = %s\n" % str(K_sizes))
        f_out.write("# Number of teeth on each wheel [S1, S2, S3, S4, S5]\n")
        f_out.write("S_sizes = %s\n" % str(S_sizes))
        f_out.write("# Number of teeth on each wheel [M1, M2]\n")
        f_out.write("M_sizes = %s\n" % str(M_sizes))
        f_out.write("\n# Pin settings for the wheels\n")
        f_out.write("K_wheels = %s\n" % str(K_wheels))
        f_out.write("S_wheels = %s\n" % str(S_wheels))
        f_out.write("M_wheels = %s\n" % str(M_wheels))
        f_out.write("\n# Indicator represents the start positions of the wheels, in "\
                "this order:\n")
        f_out.write("# [K1, K2, K3, K4, K5, M1, M2, S1, S2, S3, S4, S5]\n")
        f_out.write("indicator = %s\n\n" % str(indicator))


class gather_args(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 'arg_sequence' in namespace:
            setattr(namespace, 'arg_sequence', [])
        prev = namespace.arg_sequence
        prev.append((self.dest, values))
        setattr(namespace, 'arg_sequence', prev)


def validate_args(infile):
    if not infile.is_file():
        sys.exit('"{}" is not a file.'.format(infile))


# Main entry point when called as an executable script.
if __name__ == '__main__':

    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(
        prog='python3 lorenz.py',
        epilog=textwrap.dedent('''\
        Example:
          python3 lorenz.py --keygen <key file>
          python3 lorenz.py --encrypt <input file> <key file> <output file>
          python3 lorenz.py --decrypt <input file> <key file> <output file>
          python3 lorenz.py --readtape <input file>
          '''),
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # maincommandoption = parser.add_mutually_exclusive_group()
    parser.add_argument('--keygen', action=gather_args, nargs=1,
                        metavar='<key file>',
                        help='''Creates a random key file with normal SZ40 teeth counts and sets random indicators. Edit the file to suit.''')

    parser.add_argument('--encrypt', action=gather_args, nargs=3,
                        metavar=('<input file>', '<key file>', '<output file>'),
                        help='''Encode ASCII plaintext to Baudot code (5 bits per byte) and encrypt with wheel settings in key file, writing ciphertext to output file.''')

    parser.add_argument('--decrypt', action=gather_args, nargs=3,
                        metavar=('<input file>', '<key file>', '<output file>'),
                        help='''Decrypt the input file with wheel settings in key file, decode from Baudot code and and output ASCII plaintext to output file.''')

    parser.add_argument('--readtape', action=gather_args, nargs=1,
                        metavar='<input file>',
                        help='''Read input file in Baudot code and display ASCII equivalent.''')


    # Parse the command-line arguments. Need to create empty arg_sequence
    # in case no command-line arguments were included.
    args = parser.parse_args()
    if not 'arg_sequence' in args:
        setattr(args, 'arg_sequence', [])
    cmd = ''
    opt = ''


    if len(args.arg_sequence) == 1:
        cmd = args.arg_sequence[0][0]
        opt = args.arg_sequence[0][1]
    else:
        sys.stderr.write("Wrong options!\n")
        exit(1)


    if cmd == 'keygen':
        key_file = opt[0]
        K_sizes = [23, 26, 29, 31, 41]
        S_sizes = [59, 53, 51, 47, 43]
        M_sizes = [61, 37]
        keygen_randombuf = '{:0501b}'.format(randgen.getrandbits(573))
        K_wheels = [[], [], [], [], []]
        S_wheels = [[], [], [], [], []]
        M_wheels = [[], []]
        indicator = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(len(K_sizes)):
            K_wheels[i] = list(map(int, list(keygen_randombuf[:K_sizes[i]])))
            keygen_randombuf = keygen_randombuf[K_sizes[i]:]
            indicator[i] = int(keygen_randombuf[:6], 2) % K_sizes[i]
            keygen_randombuf = keygen_randombuf[6:]
        for i in range(len(M_sizes)):
            M_wheels[i] = list(map(int, list(keygen_randombuf[:M_sizes[i]])))
            keygen_randombuf = keygen_randombuf[M_sizes[i]:]
            indicator[i + 5] = int(keygen_randombuf[:6], 2) % M_sizes[i]
            keygen_randombuf = keygen_randombuf[6:]
        for i in range(len(S_sizes)):
            S_wheels[i] = list(map(int, list(keygen_randombuf[:S_sizes[i]])))
            keygen_randombuf = keygen_randombuf[S_sizes[i]:]
            indicator[i + 7] = int(keygen_randombuf[:6], 2) % S_sizes[i]
            keygen_randombuf = keygen_randombuf[6:]
        write_keyfile(key_file, K_sizes, S_sizes, M_sizes, K_wheels, S_wheels, M_wheels, indicator)
        print("New key data written to", key_file)


    elif cmd == 'encrypt':
        input_file = Path(opt[0])
        key_file = Path(opt[1])
        output_file = opt[2]
        validate_args(input_file)
        validate_args(key_file)
        with key_file.open('r') as key_file_contents:
            exec(key_file_contents.read())
        input_ascii = []
        with input_file.open('rb') as f_input:
            while f_input.peek():
                input_ascii.append(ord(f_input.read(1)))

        input_baudot = ascii2tty(input_ascii)

        print("Encrypting...")
        cipher = LorenzCipher(K_wheels, S_wheels, M_wheels, indicator)

        ciphertext = cipher.crypt(input_baudot)

        with open(output_file, 'w') as f_out:
            f_out.write(ciphertext)
        print("Encrypted message written to: ", output_file)


    elif cmd == 'decrypt':
        input_file = Path(opt[0])
        key_file = Path(opt[1])
        output_file = opt[2]
        validate_args(input_file)
        validate_args(key_file)
        with open(key_file, 'r') as key_file_contents:
            exec(key_file_contents.read())
        input_ciphertext = []
        with input_file.open('rb') as f:
            while f.peek():
                input_ciphertext.append(f.read(1))

        print("Decrypting...")

        cipher = LorenzCipher(K_wheels, S_wheels, M_wheels, indicator)

        plaintext_baudot = cipher.crypt(input_ciphertext)

        plaintext_ascii = tty2ascii(plaintext_baudot)

        with open(output_file, 'w') as f_out:
            f_out.write(plaintext_ascii)
        print("Decrypted message written to: ", output_file)


    elif cmd == 'readtape':
        baudot_file = Path(opt[0])
        validate_args(baudot_file)
        print("Reading TTY tape file...")
        with open(baudot_file, 'r') as f_in:
            bcode = f_in.read()
        print(tty2ascii(bcode))


    else:
        sys.stderr.write("Wrong options!\n")
        exit(1)
