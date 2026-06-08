import networkx as nx


def build_call_graph(root_node):

    graph = nx.DiGraph()

    def traverse(node, current_function=None):
        next_function = current_function

        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")

            if name_node:
                func_name = name_node.text.decode()
                graph.add_node(func_name)
                next_function = func_name

        elif node.type == "call":
            func = node.child_by_field_name("function")

            if func and current_function:
                called_function = func.text.decode()
                graph.add_edge(current_function, called_function)

        for child in node.children:
            traverse(child, next_function)

    traverse(root_node, None)

    return graph