def extract_functions(node):
    functions = []

    if node.type == "function_definition":
        name_node = node.child_by_field_name("name")
        if name_node:
            # Extract parameter names
            params = []
            parameters_node = node.child_by_field_name("parameters")
            if parameters_node:
                for child in parameters_node.children:
                    if child.type == "identifier":
                        params.append(child.text.decode())
                    elif child.type in (
                        "default_parameter", "typed_parameter",
                        "typed_default_parameter"
                    ):
                        param_name = child.child_by_field_name("name")
                        if param_name:
                            params.append(param_name.text.decode())
                        elif child.children:
                            params.append(child.children[0].text.decode())
                    elif child.type == "list_splat_pattern":
                        params.append("*" + child.text.decode().lstrip("*"))
                    elif child.type == "dictionary_splat_pattern":
                        params.append("**" + child.text.decode().lstrip("*"))

            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1

            functions.append({
                "name": name_node.text.decode(),
                "parameters": params,
                "line_count": end_line - start_line + 1,
                "start_line": start_line,
                "start_column": node.start_point[1],
                "end_line": end_line,
                "end_column": node.end_point[1]
            })

    for child in node.children:
        functions.extend(extract_functions(child))

    return functions