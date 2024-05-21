import networkx as nx
import json
import matplotlib.pyplot
import random
import math
import os


def read_input():
    config_file = open("config.json")
    config = json.load(config_file)
    config_file.close()

    G = nx.Graph()
    input_graph_file = open(config["input"], "r")
    lines = input_graph_file.readlines()
    number_of_nodes = int(lines[0])

    for i in range(number_of_nodes):
        G.add_node(i)

    lines = lines[1:]
    for line in lines:
        node1, node2 = line.split(" ")
        node1 = int(node1)
        node2 = int(node2)
        G.add_edge(node1, node2)
    input_graph_file.close()

    complement = nx.complement(G)

    return config, G, complement


def calculate_node_degrees(graph: nx.graph):
    degrees = {}
    for node in graph.nodes:
        degrees[node] = len(list(graph[node]))
    nx.set_node_attributes(graph, degrees, name="degree")


def update_pheromone_for_edge(graph: nx.graph, node1, node2, value):
    nx.set_edge_attributes(graph, {(node1, node2): {"pheromone": value}})


def init_pheromones(graph, value):
    pheromones = {}
    for edge in graph.edges:
        pheromones[edge] = value
    nx.set_edge_attributes(graph, pheromones, name="pheromone")


def calculate_probabilities(
    graph: nx.graph,
    complement_graph: nx.graph,
    alpha,
    beta,
    possible_next_nodes,
    current_node,
):
    probabilities = []
    sum = 0

    for node in possible_next_nodes:
        product = math.pow(
            complement_graph.edges[current_node, node].get("pheromone"), alpha
        ) * math.pow(graph.nodes[node].get("degree"), beta)
        probabilities.append(product)
        sum += product

    return [p / sum for p in probabilities]


def generate_solution(graph: nx.graph, complement_graph: nx.graph, alpha, beta):
    unvisited_nodes = list(graph.nodes)
    solution = []
    current_color_set = []
    excluded_nodes_from_color = set()
    current_node = None

    while unvisited_nodes:
        if len(current_color_set) == 0:
            current_node = random.choice(unvisited_nodes)
            print(f"Chosen new START node-----------------: {current_node}")
            current_color_set.append(current_node)

        neighbours = list(complement_graph[current_node])
        adjacent_nodes_in_gaph_to_color = set(graph[current_node])
        excluded_nodes_from_color = excluded_nodes_from_color.union(
            adjacent_nodes_in_gaph_to_color
        )
        possible_next_nodes = []
        for neighbour in neighbours:
            if (
                neighbour in unvisited_nodes
                and neighbour not in excluded_nodes_from_color
            ):
                possible_next_nodes.append(neighbour)
        print(f"neighbours: {neighbours}")
        print(f"unvisited_noeds: {unvisited_nodes}")
        print(f"possible_next_nodes: {possible_next_nodes}")
        unvisited_nodes.remove(current_node)
        if len(possible_next_nodes) == 0:
            solution.append(current_color_set)
            current_color_set = []
            excluded_nodes_from_color = set()

        else:
            probabilities = calculate_probabilities(
                graph, complement_graph, alpha, beta, possible_next_nodes, current_node
            )
            next_node = random.choices(possible_next_nodes, probabilities)[0]
            print(f"Chosen next node: {next_node}")
            current_color_set.append(next_node)
            current_node = next_node

    return solution


def fitness(solution):
    sum = 0
    for color_set in solution:
        sum += math.pow(len(color_set), 2)
    return sum


def update_pheromones(
    complement_graph: nx.graph, solutions, pheromone_evaporation_rate
):
    for u, v in complement_graph.edges:
        value_after_evaporation = (
            1 - pheromone_evaporation_rate
        ) * complement_graph.edges[u, v].get("pheromone")
        update_pheromone_for_edge(
                    complement_graph,
                    u,
                    v,
                    value_after_evaporation,
                )

    for solution in solutions:
        quality = fitness(solution)
        for color_set in solution:
            for i in range(1, len(color_set) - 1):
                updated_pheromone_value = (
                    complement_graph.edges[color_set[i], color_set[i - 1]].get(
                        "pheromone"
                    )
                    + quality
                )
                update_pheromone_for_edge(
                    complement_graph,
                    color_set[i - 1],
                    color_set[i],
                    updated_pheromone_value,
                )


def logging(complement_graph, solutions, log_dir, iteration, global_best):
    log_solutions = {}
    log_solutions["solutions"] = solutions
    log_solutions["global_best"] = global_best

    file_solutions = f"{log_dir}/{iteration}/solutions.json"
    file_pheromone_graph = f"{log_dir}/{iteration}/pheromone_graph.json"
    os.makedirs(os.path.dirname(file_solutions), exist_ok=True)
    os.makedirs(os.path.dirname(file_pheromone_graph), exist_ok=True)

    with open(file_solutions, "w") as outfile:
        json.dump(log_solutions, outfile)
    with open(file_pheromone_graph, "w") as outfile:
        json.dump(nx.node_link_data(complement_graph), outfile)


def ACORLF(
    graph: nx.graph,
    complement_graph: nx.graph,
    antcount,
    log_dir,
    max_iter=100,
    alpha=2,
    beta=4,
    pheromone_evaporation_rate=0.3,
    initial_pheromone_value=1,
):
    init_pheromones(complement_graph, initial_pheromone_value)
    calculate_node_degrees(graph)

    best_solution = []
    best_solution_quality = 0
    for iteration in range(max_iter):
        solutions = []
        for _ in range(antcount):
            solution = generate_solution(graph, complement_graph, alpha, beta)
            quality = fitness(solution)
            if quality > best_solution_quality:
                best_solution_quality = quality
                best_solution = solution          
            solutions.append(solution)
        print(f"{best_solution}\    {best_solution_quality}")
        update_pheromones(complement_graph, solutions, pheromone_evaporation_rate)

        logging(complement_graph, solutions, log_dir, iteration, best_solution)
        # file_pheromone_graph = f"{log_dir}/{iteration}/pheromone_graph.json"

        # os.makedirs(os.path.dirname(file_pheromone_graph), exist_ok=True)

        # with open(file_pheromone_graph, "w") as outfile:
        #     json.dump(nx.node_link_data(complement_graph), outfile)

    return best_solution


def main():
    config, graph, complement_graph = read_input()
    # u, v = graph.edges[(0,1)]
    # print(f'{u} {v}')
    # print(graph.edges[0,1])
    ACORLF(graph, complement_graph, 2, "./logs", max_iter=4, initial_pheromone_value=100)
    # fig = matplotlib.pyplot.figure()
    # nx.draw_networkx(complement_graph, ax=fig.add_subplot())
    # fig.savefig(f'{config["graph_drawings_library"]}draw.png')


if __name__ == "__main__":
    main()
