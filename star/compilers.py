# Compile abstract syntax tree to generate intermediary code
def compile_to_intermediate(tree):
    code = compile_source_node(tree, depth=0, indent=0) + '\n'
    code += f"print(_STAR_source_{0})\n"
    return code

# Recursively compile a source node in an abstract syntax tree at a particular depth and indentation level,
# Returns code which assigns a value to a string _STAR_source_<depth>
def compile_source_node(node, depth, indent):
    # The first line is indented by the caller
    code = f"# Begin code at depth {depth} with indentation level {indent}\n"
    # Add a line of code, format the line for indentation and end with a new line character
    def append_code(code_line):
        nonlocal code, indent
        code += f"{' '*4*indent}{code_line}\n"

    source_var = '_STAR_source_'
    append_code(f"{source_var}{depth} = ''")
    add_new_line = False
    for child in node['body']:
        # Separate each child's output string by a new line
        if add_new_line:
            append_code(f"{source_var}{depth} += '\\n'")
        else:
            add_new_line = True

        if child['id'] == 'TEXT':
            append_code(f"{source_var}{depth} += {repr(child['body'])}")
        elif child['id'] == 'SUB':
            sub_var = '_STAR_sub_'
            append_code(f"{sub_var}{depth} = ''")
            append_code(compile_source_node(child['body'], depth + 1, indent))
            append_code(f"{sub_var}{depth} = {source_var}{depth+1}")
            for rule in child['rules']:
                old = rule[0]
                new = rule[1]
                append_code(f"{sub_var}{depth} = {sub_var}{depth}.replace({old}, {new})")
            append_code(f"{source_var}{depth} += {sub_var}{depth}")
        elif child['id'] == 'RPT':
            rpt_var = '_STAR_rpt_'
            delim_flag_var = '_STAR_rpt_delim_'
            append_code(f"{rpt_var}{depth} = ''")
            append_code(f"{delim_flag_var}{depth} = False")
            append_code(child['init'])
            append_code(f"while {child['cond']}:")
            append_code(f"    " + compile_source_node(child['body'], depth + 1, indent + 1))
            append_code(f"    {source_var}{depth+1} = {source_var}{depth+1}")
            append_code(f"    if {delim_flag_var}{depth}:")
            append_code(f"        {rpt_var}{depth} += {child['delimiter']}")
            append_code(f"    {rpt_var}{depth} += {source_var}{depth+1}")
            append_code(f"    {child['update']}")
            append_code(f"    {delim_flag_var}{depth} = True")
            append_code(f"{source_var}{depth} += {rpt_var}{depth}")
        else:
            append_code(f"# {child['id']} abstract syntax tree node not recognized by compiler")
    # The last line doesn't end with a new line, the caller can add it if necessary
    code += f"{' '*4*indent}# End code at depth {depth} with indentation level {indent}"
    return code