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

# Функция для визуализации графа
def draw_topology(G):
    pos = nx.spring_layout(G)  # Позиционирование узлов
    labels = nx.get_node_attributes(G, 'label')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=1000, node_color="skyblue", font_size=10, font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")
    plt.title("Network Topology")
    plt.show()

# Основная часть скрипта
filename = 'network_data.csv'  # Укажите путь к вашему CSV-файлу
network_data = read_network_data(filename)
G = create_network_topology(network_data)
draw_topology(G)
