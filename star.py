import argparse
import sys
import parsy

# Main function which gets called to run the script
def main():
    args = get_args()
    intermediate = parse_to_intermediate()
    # If intermediate flag is set, print the intermediate python code
    if args.intermediate:
        print(intermediate)
        print()
    exec_intermediate(intermediate)

# Get command line arguments
def get_args():
    argparser = argparse.ArgumentParser(
        description='''Substitute Text and Repeat (STAR)
    Parses input text marked with substitution and repetition commands to produce a formatted output.''',
        epilog='''Substitute commands are of the form:
    <SUB* 'old_string_1' => 'new_string', 'old_string_2' => f'f-string'>
    Text on which to perform substitution
    <*SUB>
    where the replacement for the old string can be any string literal.

    Repeat commands are of the form
    <RPT* `init` `condition` `increment` delimiter>
    Text we want to repeat
    <*RPT>
    where init, condition, and increment are all snippets of python code and the delimiter is any string literal.

    The marked up input is used to generate intermediary python code which is executed to produce the final output.

    Each SUB or RPT element must be on its own line.
    ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    argparser.add_argument('-i', '--intermediate', action='store_true',
        help='output intermediate python code prior to final output.')

    return argparser.parse_args()

# Parse input to generate intermediary code
def parse_to_intermediate():
    source = sys.stdin.read()
    source = source.encode()
    code = 'import sys\n'
    code += f'sys.stdout.buffer.write({source})'

    # My little parsing sandbox

    # My little parsing sandbox

    return code

# Execute intermediary code
def exec_intermediate(code):
    # Execute code in its own scope
    exec(code, {}, {})

# Run main if the script is executed
if __name__ == "__main__":
    main()