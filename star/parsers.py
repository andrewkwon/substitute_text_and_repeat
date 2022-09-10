import parsy
import ast

# Generates a parser for a block of source, which is a sequence of blocks and text lines
@parsy.generate
def source_block():
    elements = yield (text_line | sub_block | rpt_block).sep_by(parsy.string('\n'))
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
    ws = optional_whitespace
    # Open rpt tag
    yield ws >> parsy.string('<RPT*')
    init = yield ws >> (code_literal | parsy.string('')) << ws << parsy.string('|')
    cond = yield ws >> (condition_literal | parsy.string('')) << ws << parsy.string('|')
    update = yield ws >> (code_literal | parsy.string('')) << ws << parsy.string('|')
    delimiter = yield ws >> string_literal
    yield ws >> parsy.string('>') >> parsy.string('\n')
    # Enclosed source block
    body = yield source_block << parsy.string('\n')
    # Close rpt tag
    yield ws >> parsy.string('<*RPT>')
    return {'id': 'RPT', 'init': init, 'cond': cond, 'update': update, 'delimiter': delimiter, 'body': body}

# Generates a parser for optional whitespace
@parsy.generate('optional whitespace')
def optional_whitespace():
    ws = yield (parsy.string('\n').should_fail('no new line') >> parsy.regex(r'[\s]')).many().concat()
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
@parsy.generate
def code_literal():
    single_ticked = parsy.string('`') >> parsy.regex('[^`\n]').many().concat() << parsy.string('`')
    double_ticked = parsy.string('``') >> parsy.regex('[^`\n]|`(?!`)').many().concat() << parsy.string('``')
    # Need to check for double tick first
    code = yield double_ticked | single_ticked
    (valid, err) = validate_syntax(code)
    if not valid:
        yield parsy.fail(f'code literal must be syntactically valid, but got {err.msg} in {err.text}')
    return code

# Generates a parser for a python while condition
@parsy.generate
def condition_literal():
    code = yield code_literal
    code_in_while = f'while({code}):\n\tpass'
    (valid, err) = validate_syntax(code_in_while)
    if not valid:
        yield parsy.fail(f'condition literal must be syntactically valid as a while condition, but got {err.msg} in {err.text}')
    return code

# Validate the syntax of the code string, returns a pair (valid bool, err error)
def validate_syntax(code):
    try:
        ast.parse(code)
    except SyntaxError as err:
        return (False, err)
    return (True, None)