from api import get_friends,names
import igraph
import time
from igraph import Graph, plot
import numpy as np
from typing import Any


def get_network(users_ids: list, as_edgelist: bool = True) -> Any:
    # Создание вершин и ребер

    vertices = []
    matrix = [[0] * len(users_ids) for _ in range(len(users_ids))]
    edges = []
    n = 0
    m = 0
    for user in users_ids:
        n += 1
        print(n, names[m])
        m += 1
        friends = get_friends(user, "")
        if 'error' in friends:
            print("deleted page")
        else:
            for friend in friends:
                if friend in users_ids:
                    edges.append((users_ids.index(user), users_ids.index(friend)))
                    matrix[users_ids.index(user)][users_ids.index(friend)] = 1
        friends = []
    if as_edgelist:
        return edges
    else:
        return matrix


def plot_graph(edges: list, vertices: list = []) -> None:
    if vertices == 0:
        for i in range(len(edges)):
            vertices.append(i)
    print("строим график")
    g = Graph(vertex_attrs={"label": vertices},
              edges=edges, directed=False)
    # Задаем стиль отображения графа
    N = len(vertices)
    visual_style = {}
    visual_style["layout"] = g.layout_fruchterman_reingold(
        maxiter=1000,
        area=N**3,
        repulserad=N**3)
    g.simplify(multiple=True, loops=True)
    N = len(vertices)
    visual_style = {
        "vertex_size": 30,
        "bbox": (2000, 2000),
        "margin": 100,
        "vertex_label_dist": 3,
        "vertex_label_size": 25,
        "edge_color": "gray",
        "autocurve": True,
        "layout": g.layout_fruchterman_reingold(
            maxiter=100000,
            area=N ** 2,
            repulserad=N ** 2)
    }

    clusters = g.community_multilevel()
    pal = igraph.drawing.colors.ClusterColoringPalette(len(clusters))
    g.vs['color'] = pal.get_many(clusters.membership)
    plot(g, **visual_style)


a = int(input("введите id пользователя для друзей которого вы хотите сделать график "))
users, names = get_friends(a, "name"), names(a)
print("У", len(users), "друзей\n\n")
ids = []
for i in range(len(users)):
    ids.append(users[i]['id'])
ed = get_network(ids)
plot_graph(ed, names)