import argparse
import sys
import parsy
import ast

# Main function which gets called to run the script
def main():
    args = get_args()
    intermediate = parse_to_intermediate()
    # If intermediate flag is set, print the intermediate python code
    if args.intermediate:
        print("```python")
        print(intermediate)
        print("```")
        print()

    (valid, err) = validate_syntax(intermediate)
    if valid:
        exec_intermediate(intermediate)
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

Repeat commands are of the form
<RPT* `init`; `condition`; `increment` | delimiter>
Text we want to repeat
<*RPT>
where init, condition, and increment are all snippets of python code and the delimiter is any string literal.
The condition must be valid as a python while condition.

The marked up input is used to generate intermediary python code which is executed to produce the final output.

Each SUB or RPT element must be on its own line.''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    argparser.add_argument('-i', '--intermediate', action='store_true',
        help='output intermediate python code prior to final output.')

    return argparser.parse_args()

# Parse input to generate intermediary code
def parse_to_intermediate():
    source = sys.stdin.read()
    # We expect each line to end with a new line character, so we add one where the input ends
    source += '\n'

    # For now we're just echoing back the file contents
    code = 'import sys\n'
    code += f'sys.stdout.buffer."write({source.encode()})'

    print("***PARSING SANDBOX***")
    parser = sub_block
    print(parser.parse(source))
    print("***PARSING SANDBOX***")
    print()

    return code

# Generates a parser for a block of source, which is a sequence of blocks
@parsy.generate
def source_block():
    pass

# Generates a parser for a block of pure text
@parsy.generate
def text_block():
    result = yield parsy.any_char.many().concat()
    return result

# Generates a parser for a substitution block surrounded by SUB tags
@parsy.generate
def sub_block():
    ws = parsy.whitespace.optional()
    yield ws >> parsy.string('<SUB*')
    result = yield parsy.any_char.many().concat()
    return result

# Generates a parser for a repetition block surrounded by RPT tags
@parsy.generate
def rpt_block():
    pass

# Generates a parser for a python non-multi-line string literal,
# For simplicity:
# doesn't check that bytestrings only use ascii characters,
# doesn't check for escape sequences other than the escaped quote,
# Based on https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals
@parsy.generate
def string_literal():
    string_prefix = parsy.string_from("r", "u", "R", "U", "f", "F",
        "fr", "Fr", "fR", "FR", "rf", "rF", "Rf", "RF")
    bytes_prefix = parsy.string_from("b", "B",
        "br", "Br", "bR", "BR", "rb", "rB", "Rb", "RB")

    pass

# Validate the syntax of the code string, returns a pair (valid bool, err error)
def validate_syntax(code):
    try:
        ast.parse(code)
    except SyntaxError as err:
        return (False, err)
    return (True, None)

# Execute intermediary code
def exec_intermediate(code):
    # Execute code in its own scope
    exec(code, {}, {})

# Run main if the script is executed
if __name__ == "__main__":
    main()