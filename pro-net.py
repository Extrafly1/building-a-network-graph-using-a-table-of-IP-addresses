import csv
import ipaddress
import networkx as nx
import matplotlib.pyplot as plt

# Функция для чтения таблицы из CSV-файла
def read_network_data(filename):
    network_data = []
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            network_data.append({
                'Network address': row['Network address'],
                'Subnet mask': row['Subnet mask'],
                'Gateway': row['Gateway'],
                'Interface': row['Interface'],
                'Metric': int(row['Metric'])
            })
    return network_data

# Функция для определения типа узла (Router, Switch, PC, Internet)
def determine_node_types(G, network_data):
    node_types = {}
    ip_ranges = {}
    gateways = set(entry['Gateway'] for entry in network_data)
    
    for entry in network_data:
        network_address = entry['Network address']
        subnet_mask = entry['Subnet mask']
        
        # Определение диапазона IP для коммутаторов (Switch)
        if network_address not in gateways and G.degree(network_address) > 0:
            net = ipaddress.IPv4Network(f"{network_address}/{subnet_mask}", strict=False)
            ip_ranges[network_address] = f"{net.network_address} - {net.broadcast_address}"
        
    for node in G.nodes():
        if node == "0.0.0.0":
            node_types[node] = 'Internet'
        elif node in gateways:
            node_types[node] = 'Router'
        elif node in ip_ranges:
            node_types[node] = 'Switch'
        else:
            node_types[node] = 'PC'
    
    return node_types, ip_ranges

# Функция для добавления ПК к узлам типа Switch или Router
def add_pcs_to_leaves(G, node_types):
    pc_count = 1
    for node in list(G.nodes()):
        if node_types[node] in ['Switch'] and node != "0.0.0.0":
            # Добавляем ПК к текущему узлу, если он не 0.0.0.0
            pc_node = f"PC_{pc_count}"
            G.add_node(pc_node, label=pc_node)
            G.add_edge(node, pc_node)
            node_types[pc_node] = 'PC'
            pc_count += 1
    return node_types

# Функция для создания графа сети
def create_network_topology(network_data):
    G = nx.Graph()
    
    for entry in network_data:
        network_address = entry['Network address']
        gateway = entry['Gateway']
        metric = entry['Metric']
        
        # Добавляем узлы (сети)
        G.add_node(network_address, label=network_address)
        G.add_node(gateway, label=gateway)
        
        # Добавляем ребро между сетью и шлюзом с весом (метрикой)
        G.add_edge(network_address, gateway, weight=metric)
    
    return G

# Функция для визуализации графа с указанием типов устройств и диапазона IP-адресов для Switch
def draw_topology(G, node_types, ip_ranges):
    pos = nx.spring_layout(G)  # Позиционирование узлов
    labels = {}
    for node in G.nodes():
        if node_types[node] == 'Switch':
            labels[node] = f"{node}\n({node_types[node]})\n{ip_ranges[node]}"
        else:
            labels[node] = f"{node}\n({node_types[node]})"

    edge_labels = nx.get_edge_attributes(G, 'weight')
    
    color_map = {
        'Router': 'red',
        'Switch': 'blue',
        'PC': 'green',
        'Internet': 'orange'
    }
    node_colors = [color_map[node_types[node]] for node in G.nodes()]

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=1000, node_color=node_colors, font_size=10, font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")
    plt.title("Network Topology with Device Types and IP Ranges for Switches")
    plt.show()

# Основная часть скрипта
filename = 'network_data.csv'  # Укажите путь к вашему CSV-файлу
network_data = read_network_data(filename)
G = create_network_topology(network_data)
node_types, ip_ranges = determine_node_types(G, network_data)
node_types = add_pcs_to_leaves(G, node_types)  # Добавление ПК к узлам типа Switch и Router
draw_topology(G, node_types, ip_ranges)
