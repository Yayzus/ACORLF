import json
import networkx as nx
import matplotlib.pyplot as plt
import os

number_of_epoch = len(os.listdir("./logs"))
print(number_of_epoch)

pos = []
time = 0.9

def normalize_pheromones(G: nx.graph):
    pheromones = []
    for u, v in G.edges:
        pheromones.append(G.edges[u, v].get("pheromone"))

    maximum = max(pheromones)
    minimum = min(pheromones)
    pheromones = [((pheromone-minimum)/(maximum-minimum))*3 + 0.1  for pheromone in pheromones]
    return pheromones

fig, (subpltL, subpltR) = plt.subplots(1,2, figsize=(50, 75))
colors_to_choose_from = ["blue", "red", "green", "orange", "yellow"]
number_of_nodes = 0
colors = []
width_of_lines = []
for i in range(number_of_epoch):
    graph_data_file = open(f"./logs/{i}/pheromone_graph.json")
    graph_data = json.load(graph_data_file)
    G = nx.node_link_graph(graph_data)
    G_original = nx.complement(G)
    if i == 0:
        pos = nx.circular_layout(G)
        number_of_nodes = len(list(G.nodes))
        colors = ["black" for _ in range(number_of_nodes)]
        width_of_lines =[0.1 for _ in range(number_of_nodes)]

        subpltR.set_title('Global best solution')
        nx.draw(G_original, pos, node_color= 'gray', width=0.3, ax=subpltR, with_labels=True)
        plt.pause(time/3)

 
    subpltL.clear()
    subpltL.set_title(f'Epoch {i+1}')
    nx.draw(G, pos, node_color=colors, width=width_of_lines, ax=subpltL, with_labels=True)
    plt.pause(time)

    solutions_file = open(f"./logs/{i}/solutions.json", "r")
    solutions_data = json.load(solutions_file)
    solutions = solutions_data['solutions']
    global_best = solutions_data['global_best']

    for idx, solution in enumerate(solutions):
        plot_title = f'Epoch {i+1}, Ant {idx+1}'
        subpltL.set_title(plot_title)
        color_index = 0
        for color_set in solution:
            # print('hello')
            current_color = colors_to_choose_from[color_index]
            for node in color_set:
                # print(current_color)
                colors[node] = current_color
                subpltL.clear()
                subpltL.set_title(plot_title)
                nx.draw(G, pos, node_color = colors, width = width_of_lines, ax = subpltL, with_labels=True)
                plt.pause(time)
            color_index += 1
        plt.pause(2*time)
        colors = ["black" for _ in range(number_of_nodes)]
        subpltL.clear()
        subpltL.set_title(plot_title)
        nx.draw(G, pos, node_color = colors, width = width_of_lines, ax = subpltL, with_labels=True)
        plt.pause(time)
    
    best_colors = ["black" for _ in range(number_of_nodes)]
    best_color_idx = 0
    for color_set in global_best:
        current_color = colors_to_choose_from[best_color_idx]
        for node in color_set:
            best_colors[node] = current_color
        best_color_idx += 1
    subpltR.clear()
    subpltR.set_title('Global best solution')
    nx.draw(G_original, pos, node_color = best_colors, width = 0.3, ax = subpltR, with_labels=True)
    plt.pause(time/3)

    width_of_lines = normalize_pheromones(G)
    nx.draw(G, pos, node_color = colors, width = width_of_lines, ax = subpltL, with_labels=True)
    plt.pause(time)

# print(colors)
plt.show()
