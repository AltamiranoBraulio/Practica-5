import matplotlib.pyplot as plt           # Importa la librería para graficar
import networkx as nx                     # Importa la librería para grafos
from matplotlib.widgets import Button      # Importa el widget de botón para matplotlib
import sys                                # Importa sys para salir del programa
from collections import defaultdict        # Importa defaultdict para agrupar nodos
import random                             # Importa random para generar números aleatorios

class KruskalSimulator:
    def __init__(self):
        self.graph = nx.Graph()           # Crea un grafo vacío
        self.edges = []                   # Lista para almacenar las aristas
        self.steps = []                   # Lista para los pasos del algoritmo
        self.current_step = 0             # Índice del paso actual
        self.fig, self.ax = plt.subplots(figsize=(12, 8))  # Crea la figura para graficar
        plt.subplots_adjust(bottom=0.2)   # Ajusta el espacio inferior para los botones
        
        self.nodes = [chr(i) for i in range(65, 91)]  # Genera nodos de 'A' a 'Z'
        for node in self.nodes:
            self.graph.add_node(node)     # Añade cada nodo al grafo
        
        self.create_random_connected_graph()  # Crea un grafo aleatorio y conexo
        
        # Crea los botones de control para la simulación
        self.ax_prev = plt.axes([0.3, 0.05, 0.1, 0.075])
        self.ax_next = plt.axes([0.6, 0.05, 0.1, 0.075])
        self.btn_prev = Button(self.ax_prev, 'Anterior')
        self.btn_next = Button(self.ax_next, 'Siguiente')
        self.btn_prev.on_clicked(self.prev_step)   # Asocia el botón "Anterior" a la función prev_step
        self.btn_next.on_clicked(self.next_step)   # Asocia el botón "Siguiente" a la función next_step
        
    def create_random_connected_graph(self):
        """Crea un grafo conexo aleatorio con nodos de A a Z"""
        nodes = self.nodes.copy()         # Copia la lista de nodos
        random.shuffle(nodes)             # Mezcla los nodos aleatoriamente
        
        # Crea un árbol de expansión mínimo para asegurar la conexidad
        for i in range(1, len(nodes)):
            weight = random.randint(1, 100)   # Peso aleatorio
            self.graph.add_edge(nodes[i-1], nodes[i], weight=weight)  # Añade arista
            self.edges.append((nodes[i-1], nodes[i], weight))         # Guarda la arista
        
        # Añade aristas extra para mayor complejidad
        extra_edges = random.randint(10, 30)
        for _ in range(extra_edges):
            u, v = random.sample(nodes, 2)   # Selecciona dos nodos distintos
            if not self.graph.has_edge(u, v):    # Si no existe la arista
                weight = random.randint(1, 100)
                self.graph.add_edge(u, v, weight=weight)
                self.edges.append((u, v, weight))
    
    def find_parent(self, parent, node):
        """Encuentra el padre de un nodo (Union-Find)"""
        if parent[node] == node:
            return node
        return self.find_parent(parent, parent[node])
    
    def union(self, parent, rank, u, v):
        """Une dos conjuntos en Union-Find"""
        u_root = self.find_parent(parent, u)
        v_root = self.find_parent(parent, v)
        
        if rank[u_root] < rank[v_root]:
            parent[u_root] = v_root
        elif rank[u_root] > rank[v_root]:
            parent[v_root] = u_root
        else:
            parent[v_root] = u_root
            rank[u_root] += 1
    
    def print_step_details(self, step):
        """Imprime los detalles del paso actual en consola"""
        print("\n" + "="*80)
        print(f"PASO {self.current_step + 1}/{len(self.steps)}".center(80))
        print("="*80)
        
        if step['edge'] is not None:
            u, v, w = step['edge']
            print(f"\nArista actual: {u}-{v} (Peso: {w})")
            print(f"Acción: {step['action'].upper()}")
            if step['result'] is not None:
                print(f"Resultado: {step['result'].upper()}")
        else:
            print("\nPROCESO COMPLETADO!")
        
        print(f"\nCosto acumulado del MST: {step['total_cost']}")
        print(f"Aristas en MST: {len(step['current_mst'])}/{len(self.nodes)-1}")
        
        # Muestra las aristas actuales del MST
        print("\nAristas en el MST actual:")
        if step['current_mst']:
            for u, v, w in step['current_mst']:
                print(f"  {u}-{v} (Peso: {w})")
        else:
            print("  (ninguna)")
        
        # Muestra la estructura Union-Find
        print("\nEstructura Union-Find:")
        parent = step['parent']
        rank = step['rank']
        
        components = defaultdict(list)
        for node in self.nodes:
            root = self.find_parent(parent, node)
            components[root].append(node)
        
        for root, nodes in components.items():
            print(f"  Componente con raíz {root}: {', '.join(nodes)} (rango: {rank[root]})")
        
        print("="*80 + "\n")
    
    def run_kruskal(self, max_tree=False):
        """Ejecuta el algoritmo de Kruskal y guarda los pasos"""
        self.steps = []                   # Reinicia los pasos
        result = []                       # MST actual
        total_cost = 0                    # Costo acumulado
        
        # Ordena las aristas por peso (ascendente o descendente)
        sorted_edges = sorted(self.edges, key=lambda x: x[2], reverse=max_tree)
        
        parent = {node: node for node in self.nodes}   # Inicializa padres
        rank = {node: 0 for node in self.nodes}        # Inicializa rangos
        
        print("\nINICIANDO ALGORITMO DE KRUSKAL")
        print(f"Buscando {'MÁXIMO' if max_tree else 'MÍNIMO'} árbol de expansión")
        print(f"Número total de aristas: {len(self.edges)}")
        print(f"Número total de nodos: {len(self.nodes)}")
        print(f"Aristas ordenadas por peso ({'descendente' if max_tree else 'ascendente'}):")
        for u, v, w in sorted_edges:
            print(f"  {u}-{v} (Peso: {w})")
        
        for edge in sorted_edges:
            u, v, w = edge
            u_root = self.find_parent(parent, u)
            v_root = self.find_parent(parent, v)
            
            # Guarda el estado antes de decidir
            step_info = {
                'edge': edge,
                'action': 'considerando',
                'result': None,
                'current_mst': result.copy(),
                'total_cost': total_cost,
                'parent': parent.copy(),
                'rank': rank.copy()
            }
            self.steps.append(step_info)
            
            if u_root != v_root:
                result.append(edge)
                total_cost += w
                self.union(parent, rank, u_root, v_root)
                
                step_info = {
                    'edge': edge,
                    'action': 'añadido',
                    'result': 'aceptado (no forma ciclo)',
                    'current_mst': result.copy(),
                    'total_cost': total_cost,
                    'parent': parent.copy(),
                    'rank': rank.copy()
                }
            else:
                step_info = {
                    'edge': edge,
                    'action': 'rechazado',
                    'result': 'forma ciclo',
                    'current_mst': result.copy(),
                    'total_cost': total_cost,
                    'parent': parent.copy(),
                    'rank': rank.copy()
                }
            
            self.steps.append(step_info)
        
        # Añade el paso final con el resultado completo
        final_step = {
            'edge': None,
            'action': 'completado',
            'result': 'árbol de expansión encontrado',
            'current_mst': result.copy(),
            'total_cost': total_cost,
            'parent': parent.copy(),
            'rank': rank.copy()
        }
        self.steps.append(final_step)
        
        self.current_step = 0              # Reinicia el paso actual
        self.display_step()                # Muestra el primer paso
        self.print_step_details(self.steps[self.current_step])  # Imprime detalles
    
    def display_step(self):
        """Muestra el paso actual en la visualización gráfica"""
        self.ax.clear()                    # Limpia el gráfico
        
        if self.current_step >= len(self.steps):
            self.current_step = len(self.steps) - 1
        if self.current_step < 0:
            self.current_step = 0
            
        step = self.steps[self.current_step]
        
        # Dibuja el grafo completo con aristas grises
        pos = nx.spring_layout(self.graph, seed=42)
        nx.draw_networkx_nodes(self.graph, pos, node_size=700, ax=self.ax, node_color='lightblue')
        nx.draw_networkx_labels(self.graph, pos, ax=self.ax)
        
        all_edges = [(u, v) for u, v, w in self.edges]
        nx.draw_networkx_edges(self.graph, pos, edgelist=all_edges, edge_color='gray', width=1, ax=self.ax)
        
        # Dibuja las aristas del MST en verde
        mst_edges = [(u, v) for u, v, w in step['current_mst']]
        nx.draw_networkx_edges(self.graph, pos, edgelist=mst_edges, edge_color='green', width=3, ax=self.ax)
        
        # Resalta la arista actual
        if step['edge'] is not None:
            current_edge = [(step['edge'][0], step['edge'][1])]
            if step['result'] is None:
                edge_color = 'orange'
            else:
                edge_color = 'red' if 'aceptado' in step['result'] else 'orange'
            nx.draw_networkx_edges(self.graph, pos, edgelist=current_edge, edge_color=edge_color, width=3, ax=self.ax)
        
        # Muestra los pesos de las aristas
        edge_labels = {(u, v): w for u, v, w in self.edges}
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, ax=self.ax)
        
        # Muestra información del paso
        info_text = f"Paso {self.current_step + 1}/{len(self.steps)}\n"
        if step['edge'] is not None:
            info_text += f"Arista: {step['edge'][0]}-{step['edge'][1]} (Peso: {step['edge'][2]})\n"
            info_text += f"Acción: {step['action']}\n"
            if step['result'] is not None:
                info_text += f"Resultado: {step['result']}\n"
        else:
            info_text += "Proceso completado!\n"
        
        info_text += f"Costo acumulado: {step['total_cost']}\n"
        info_text += f"Aristas en MST: {len(step['current_mst'])}/{len(self.nodes)-1}"
        
        self.ax.set_title(info_text, loc='left', fontsize=10)
        
        # Muestra la estructura union-find
        uf_text = "Estructura Union-Find:\n"
        for node in sorted(step['parent'].keys()):
            uf_text += f"{node}: padre={step['parent'][node]}, rango={step['rank'][node]}\n"
        
        plt.figtext(0.75, 0.2, uf_text, fontsize=8, bbox=dict(facecolor='white', alpha=0.5))
        
        plt.draw()
    
    def prev_step(self, event):
        self.current_step -= 1             # Retrocede un paso
        self.display_step()                # Actualiza la visualización
        self.print_step_details(self.steps[self.current_step])  # Imprime detalles
    
    def next_step(self, event):
        self.current_step += 1             # Avanza un paso
        self.display_step()                # Actualiza la visualización
        self.print_step_details(self.steps[self.current_step])  # Imprime detalles

def main_menu():
    print("\n" + "="*50)
    print("SIMULADOR DE ÁRBOL DE EXPANSIÓN - KRUSKAL".center(50))
    print("="*50)
    print("\n1. Árbol de Expansión Mínima (Minimum Spanning Tree)")
    print("2. Árbol de Expansión Máxima (Maximum Spanning Tree)")
    print("3. Salir")
    
    while True:
        try:
            choice = int(input("\nSeleccione una opción (1-3): "))  # Pide opción al usuario
            if 1 <= choice <= 3:
                return choice
            else:
                print("Por favor ingrese un número entre 1 y 3.")
        except ValueError:
            print("Entrada inválida. Por favor ingrese un número.")

def main():
    simulator = KruskalSimulator()         # Crea el simulador
    
    while True:
        choice = main_menu()               # Muestra el menú y obtiene la opción
        
        if choice == 1:
            print("\nEjecutando algoritmo de Kruskal para Árbol de Expansión Mínima...")
            simulator.run_kruskal(max_tree=False)   # Ejecuta para árbol mínimo
            plt.show()                              # Muestra la ventana gráfica
        elif choice == 2:
            print("\nEjecutando algoritmo de Kruskal para Árbol de Expansión Máxima...")
            simulator.run_kruskal(max_tree=True)    # Ejecuta para árbol máximo
            plt.show()
        elif choice == 3:
            print("\nSaliendo del simulador...")
            sys.exit()                              # Sale del programa

if __name__ == "__main__":
    main()                                          # Ejecuta el programa principal