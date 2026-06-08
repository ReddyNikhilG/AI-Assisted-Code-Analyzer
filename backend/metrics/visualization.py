import matplotlib.pyplot as plt
import networkx as nx


def visualize_graph(graph, title):

    plt.figure(figsize=(8, 6))

    nx.draw(
        graph,
        with_labels=True
    )

    plt.title(title)

    plt.show()