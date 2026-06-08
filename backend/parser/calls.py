def extract_calls(node):
    calls = []

    if node.type == "call":
        func = node.child_by_field_name("function")

        if func:
            calls.append({
                "name": func.text.decode(),
                "start_line": func.start_point[0] + 1,
                "start_column": func.start_point[1],
                "end_line": func.end_point[0] + 1,
                "end_column": func.end_point[1]
            })

    for child in node.children:
        calls.extend(extract_calls(child))

    return calls