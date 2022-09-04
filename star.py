import argparse
import sys
import parsy
import ast
import pprint

# Main function which gets called to run the script
def main():
    args = get_args()
    source = sys.stdin.read()
    # Parse the input source to an abstract syntax tree
    tree = source_block.parse(source)
    if args.ast:
        print("```ast")
        pprint.pprint(tree, sort_dicts=False)
        print("```\n")
    # Compile the abstract syntax tree to intermediate code
    intermediate = compile_to_intermediate(tree)
    if args.intermediate:
        print("```python")
        print(intermediate)
        print("```\n")

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
Substitution rules are applied sequentially from left to right.

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
    argparser.add_argument('-a', '--ast', action='store_true',
        help='output the generated abstract syntax tree parsed from the input source')
    argparser.add_argument('-i', '--intermediate', action='store_true',
        help='output intermediate python code prior to final output.')

    return argparser.parse_args()

# Generates a parser for a block of source, which is a sequence of blocks and text lines
@parsy.generate
def source_block():
    elements = yield (text_line | sub_block).sep_by(parsy.string('\n'))
    return {'id': 'SOURCE', 'body': elements}

# Generates a parser for a line of pure text
@parsy.generate
def text_line():
    ws = optional_whitespace
    opening_tag = parsy.string('<SUB*') | parsy.string('<RPT*')
    closing_tag = parsy.string('<*SUB>') | parsy.string('<*RPT>')
    not_tag = parsy.peek(ws >> opening_tag.should_fail('not opening tag') >> closing_tag.should_fail('not closing tag'))
    escaped_tag = parsy.string('\\') >> (opening_tag | closing_tag)
    text = yield not_tag >> (ws + (escaped_tag | parsy.string('')) + parsy.regex('[^\n]').many().concat())
    return {'id': 'TEXT', 'body': text}

# Generates a parser for a substitution block surrounded by SUB tags
@parsy.generate
def sub_block():
    ws = optional_whitespace
    # Open sub tag
    yield ws >> parsy.string('<SUB*')
    sub_rule = ((ws >> string_literal).times(1) +
        (ws >> parsy.string('=>') >> ws >> string_literal).times(1)).desc('substitution rule')
    sub_rules = yield sub_rule.sep_by(parsy.string(','))
    yield ws >> parsy.string('>') >> parsy.string('\n')
    # Enclosed source block
    body = yield source_block << parsy.string('\n')
    # Close sub tag
    yield ws >> parsy.string('<*SUB>')
    return {'id': 'SUB', 'rules': sub_rules, 'body': body}

# Generates a parser for a repetition block surrounded by RPT tags
@parsy.generate
def rpt_block():
    pass

# Generates a parser for optional whitespace
@parsy.generate('optional whitespace')
def optional_whitespace():
    ws = yield parsy.whitespace | parsy.string('')
    return ws

# Generates a parser for a python single-line string literal,
# For simplicity:
# doesn't check that bytestrings only use ascii characters,
# doesn't check for escape sequences other than the escaped quote and slash,
# Syntax from https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals
@parsy.generate('python string literal')
def string_literal():
    string_prefix = parsy.string_from("r", "u", "R", "U", "f", "F",
        "fr", "Fr", "fR", "FR", "rf", "rF", "Rf", "RF").desc('character string literal prefix')
    bytes_prefix = parsy.string_from("b", "B",
        "br", "Br", "bR", "BR", "rb", "rB", "Rb", "RB").desc('byte string literal prefix')
    prefix = yield (string_prefix | bytes_prefix | parsy.string('')).desc('string literal prefix')

    single_quoted = (parsy.string("'") +
        (parsy.string(r"\'") | parsy.string(r"\\") | parsy.regex("[^'\n]")).many().concat() +
        parsy.string("'")).desc('single-quoted string literal contents')
    double_quoted = (parsy.string('"') +
        (parsy.string(r'\"') | parsy.string(r'\\') | parsy.regex('[^"\n]')).many().concat() +
        parsy.string('"')).desc('double-quoted string literal contents')
    quoted = yield (single_quoted | double_quoted).desc('quoted string literal contents')

    return prefix + quoted

# Generates a parser for a snippet of python code
@parsy.generate('python code literal')
def code_literal():
    single_ticked = parsy.string('`') >> parsy.regex('[^`\n]').many().concat() << parsy.string('`')
    double_ticked = parsy.string('``') >> parsy.regex('[^`\n]|`(?!`)').many().concat() << parsy.string('``')
    code = yield single_ticked | double_ticked
    return code

# Compile abstract syntax tree to generate intermediary code
def compile_to_intermediate(tree):
    code = compile_source_node(tree, depth=0)
    code += f"print(_STAR_source_{0})\n"
    return code

# Recursively compile a source node in an abstract syntax tree at a particular depth,
# Returns code which assigns a value to a string _STAR_source_<depth>
def compile_source_node(node, depth):
    code = f"_STAR_source_{depth} = ''\n"
    for child in node['body']:
        if child['id'] == 'TEXT':
            code += f"_STAR_source_{depth} += {repr(child['body'])} + '\\n'\n"
        elif child['id'] == 'SUB':
            code += f"_STAR_sub_{depth} = ''\n"
            code += compile_source_node(child['body'], depth + 1)
            code += f"_STAR_sub_{depth} = _STAR_source_{depth+1}\n"
            for rule in child['rules']:
                old = rule[0]
                new = rule[1]
                code += f"_STAR_sub_{depth} = _STAR_sub_{depth}.replace({old}, {new})\n"
            code += f"_STAR_source_{depth} += _STAR_sub_{depth}\n"
    return code

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