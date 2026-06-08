def extract_imports(node):
    imports = []

    if node.type in ["import_statement", "import_from_statement"]:
        imports.append({
            "code": node.text.decode(),
            "start_line": node.start_point[0] + 1,
            "start_column": node.start_point[1],
            "end_line": node.end_point[0] + 1,
            "end_column": node.end_point[1]
        })

    for child in node.children:
        imports.extend(extract_imports(child))

    return imports