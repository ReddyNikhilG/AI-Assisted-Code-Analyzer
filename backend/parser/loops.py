def extract_loops(node):
    loops = []

    if node.type in ["for_statement", "while_statement"]:
        loops.append({
            "type": "for" if node.type == "for_statement" else "while",
            "start_line": node.start_point[0] + 1,
            "start_column": node.start_point[1],
            "end_line": node.end_point[0] + 1,
            "end_column": node.end_point[1]
        })

    for child in node.children:
        loops.extend(extract_loops(child))

    return loops


def count_loops(node):
    return len(extract_loops(node))