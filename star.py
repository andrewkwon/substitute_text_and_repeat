#!/usr/bin/env python3

import star.parsers
import star.compilers
import star.executors
import argparse
import sys
import pprint

# Main function which gets called to run the script
def main():
    args = get_args()
    source = sys.stdin.read()
    # Parse the input source to an abstract syntax tree
    tree = star.parsers.source_block.parse(source)
    if args.ast:
        print("```ast")
        pprint.pprint(tree, sort_dicts=False)
        print("```\n")
    # Compile the abstract syntax tree to intermediate code
    intermediate = star.compilers.compile_to_intermediate(tree)
    if args.intermediate:
        print("```python")
        print(intermediate)
        print("```\n")

    (valid, err) = star.parsers.validate_syntax(intermediate)
    if valid:
        star.executors.exec_intermediate(intermediate)
    else:
        print('The generated intermediate code had a syntax error:')
        print(f'{err.msg} at line {err.lineno}, column {err.offset}')
        print(f'\t{err.text}')

# Get command line arguments
def get_args():
    argparser = argparse.ArgumentParser(
        description='''Substitute Text and Repeat (STAR)
Parses input text marked with substitution and repetition commands to produce a formatted output.''',
        epilog='''Substitute commands are of the form:
<SUB* 'old_string_1' => 'new_string', 'old_string_2' => f'f-string', f'old_f_string' => 'new_string_2'>
Text on which to perform substitution
<*SUB>
where the strings can be any string literals.
Substitution rules are applied sequentially from left to right.

Repeat commands are of the form
<RPT* `init` | `condition` | `update` | delimiter>
Text we want to repeat
<*RPT>
where init, condition, and update are all snippets of python code and the delimiter is any string literal.
The condition must be valid as a python while condition.

The marked up input is used to generate intermediary python code which is executed to produce the final output.

Each SUB or RPT tag must be on its own line.''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    argparser.add_argument('-a', '--ast', action='store_true',
        help='output the generated abstract syntax tree parsed from the input source')
    argparser.add_argument('-i', '--intermediate', action='store_true',
        help='output intermediate python code prior to final output.')

    return argparser.parse_args()

# Run main if the script is executed
if __name__ == "__main__":
    main()