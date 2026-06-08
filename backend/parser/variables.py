def extract_variables(node):
    variables = []

    if node.type == "assignment":
        left = node.child_by_field_name("left")
        if not left and len(node.children) > 0:
            left = node.children[0]
        if left:
            variables.append({
                "name": left.text.decode(),
                "start_line": left.start_point[0] + 1,
                "start_column": left.start_point[1],
                "end_line": left.end_point[0] + 1,
                "end_column": left.end_point[1]
            })

    for child in node.children:
        variables.extend(extract_variables(child))

    return variables