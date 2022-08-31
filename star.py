# Substitute Text and Repeat (STAR)
# Parses input text marked up with

import argparse

parser = argparse.ArgumentParser(description='Substitute Text and Repeat (STAR)' +
    'Parses input text marked with substitution and repetition commands to produce desired output.')
parser.add_argument('-i', '--intermediate', action='store_true')

args = parser.parse_args()
print(args)

i = 0
code = 'print(3 + 4)'
# Execute code in its own scope
exec(code, {}, {})