# Compiles abstract syntax tree to generate intermediary code
def compile_to_intermediate(tree):
    builder = CodeBuilder(depth=0, indent=0)
    code = builder.compile_source_node(tree) + '\n'
    code += f"print({CodeBuilder.source_var}{0})"
    return code

# Builds a block of intermediate code
class CodeBuilder:
    source_var = '_STAR_source_'

    def __init__(self, depth, indent):
        self.code = ""
        self.depth = depth
        self.indent = indent

    # Adds a line of code, format the line for indentation and end with a new line character
    def append(self, code_line):
        self.code += f"{' '*4*self.indent}{code_line}\n"

    # Recursively compiles a source node in an abstract syntax tree at a particular depth and indentation level,
    # Returns code which assigns a value to a string named {source_var}{depth}
    def compile_source_node(self, node):
        # The first line is indented by the caller
        self.code = f"# Begin code at depth {self.depth} with indentation level {self.indent}\n"
        self.append(f"{self.source_var}{self.depth} = ''")
        add_new_line = False
        for child in node['body']:
            # Separate each child's output string by a new line
            if add_new_line:
                self.append(f"{self.source_var}{self.depth} += '\\n'")
            else:
                add_new_line = True

            # Append code based on the child type
            if child['id'] == 'TEXT':
                self.append_compiled_text_node(child)
            elif child['id'] == 'SUB':
                self.append_compiled_sub_node(child)
            elif child['id'] == 'RPT':
                self.append_compiled_rpt_node(child)
            else:
                self.append(f"# {child['id']} abstract syntax tree node not recognized by compiler")

        # The last line doesn't end with a new line, the caller can add it if necessary
        self.code += f"{' '*4*self.indent}# End code at depth {self.depth} with indentation level {self.indent}"
        return self.code

    # Compiles a text node and appends to the builder
    def append_compiled_text_node(self, node):
        self.append(f"{self.source_var}{self.depth} += {repr(node['body'])}")

    # Compiles a sub node and appends to the builder
    def append_compiled_sub_node(self, node):
        sub_var = '_STAR_sub_'
        self.append(f"{sub_var}{self.depth} = ''")
        builder = CodeBuilder(self.depth + 1, self.indent)
        self.append(builder.compile_source_node(node['body']))
        self.append(f"{sub_var}{self.depth} = {self.source_var}{self.depth+1}")
        for rule in node['rules']:
            old = rule[0]
            new = rule[1]
            self.append(f"{sub_var}{self.depth} = {sub_var}{self.depth}.replace({old}, {new})")
        self.append(f"{self.source_var}{self.depth} += {sub_var}{self.depth}")

    # Compiles a rpt node and appends to the builder
    def append_compiled_rpt_node(self, node):
        rpt_var = '_STAR_rpt_'
        delim_flag_var = '_STAR_rpt_delim_'
        self.append(f"{rpt_var}{self.depth} = ''")
        self.append(f"{delim_flag_var}{self.depth} = False")
        self.append(node['init'])
        self.append(f"while {node['cond']}:")
        builder = CodeBuilder(self.depth + 1, self.indent + 1)
        self.append(f"    " + builder.compile_source_node(node['body']))
        self.append(f"    {self.source_var}{self.depth+1} = {self.source_var}{self.depth+1}")
        self.append(f"    if {delim_flag_var}{self.depth}:")
        self.append(f"        {rpt_var}{self.depth} += {node['delimiter']}")
        self.append(f"    {rpt_var}{self.depth} += {self.source_var}{self.depth+1}")
        self.append(f"    {node['update']}")
        self.append(f"    {delim_flag_var}{self.depth} = True")
        self.append(f"{self.source_var}{self.depth} += {rpt_var}{self.depth}")
