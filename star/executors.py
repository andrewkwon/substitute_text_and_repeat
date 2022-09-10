import traceback

# Execute intermediary code
def exec_intermediate(code):
    # Execute code in its own scope
    try:
        exec(code, {}, {})
    except Exception:
        print("```python intermediate with line numbers")
        print(format_line_nums(code))
        print("```\n")
        print('Encountered an error while executing the generated intermediate code:')
        traceback.print_exc()

# Return string formatted with line numbers
def format_line_nums(string):
    lines = string.split('\n')
    for i in range(len(lines)):
        lines[i] = f'{i + 1}\t|{lines[i]}'
    return '\n'.join(lines)