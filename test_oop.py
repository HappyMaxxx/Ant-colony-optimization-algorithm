import matplotlib.pyplot as plt
import networkx as nx
import tkinter as tk
from tkinter import IntVar
import ttkbootstrap as ttk
from ttkbootstrap import Labelframe
from ttkbootstrap.toast import ToastNotification
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
from tkinter import filedialog
from PIL import Image
import numpy as np
import random
import time
import threading

from settings import *

class AntColonyApp:
    def __init__(self, root):
        self.debugging = False
        self.show_nums = True
        self.points = []
        self.dot_color = 'black'
        self.text_color = 'white'
        self.threshold_distance = 0.5
        self.img_array = None
        self.text_for_error = ''
        self.point_labels = []
        self.iteration = None
        self.distances = {}
        self.feromons = {}
        self.routes = {}
        self.ants = 0
        self.G = nx.Graph()
        self.stop_auto_iteration = False
        self.current_language = 'en'
        self.selected_var = IntVar(value=0)
        self.is_random = False

        self.window = root
        self.window.title("Ant Colony")
        self.fig = plt.Figure(figsize=(7, 5))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()

        self.frame = ttk.Frame(self.window)
        self.frame.pack(side=ttk.RIGHT, fill=ttk.BOTH, expand=False)

        self.setup_ui()
        self.update_ui_language()
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)

    def setup_ui(self):
        self.canvas.get_tk_widget().pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True, padx=10, pady=15)

        self.menu_frame = Labelframe(self.frame, padding="10")
        self.menu_frame.pack(fill="both", expand="yes", padx=10, pady=(3, 15))

        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)

        self.language_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.language_menu.add_command(label="Switch Language", command=self.switch_language)
        self.menu_bar.add_cascade(label="Language", menu=self.language_menu)

        self.start_button = ttk.Button(self.menu_frame, command=self.start_algor)
        self.choose_image_button = ttk.Button(self.menu_frame, command=self.choose_image)
        self.clear_image_button = ttk.Button(self.menu_frame, command=self.clear_image)
        self.clear_points_button = ttk.Button(self.menu_frame, command=self.clear_points)
        self.change_color_button = ttk.Button(self.menu_frame, command=self.change_dot_color)
        self.show_nums_button = ttk.Button(self.menu_frame, command=self.unshow_nums)
        self.start_new_iteration_button = ttk.Button(self.menu_frame, command=self.ant_colony)
        self.checkbutton = ttk.Checkbutton(self.menu_frame, variable=self.selected_var, onvalue=1, offvalue=0, command=self.handle_check_button)
        self.label1 = tk.Label(self.menu_frame, font=("Arial", 10, "bold"))
        self.start_auto_button = ttk.Button(self.menu_frame, command=self.start_auto)
        self.stop_auto_button = ttk.Button(self.menu_frame, command=self.stop_auto)
        self.iteration_text = tk.Label(self.menu_frame, font=("Arial", 10, "bold"))
        self.feromone_label = tk.Label(self.menu_frame, font=("Arial", 10, "bold"))
        self.num_of_options_text = tk.Label(self.menu_frame, font=("Arial", 10, "bold"))
        self.num_of_options = ttk.Label(self.menu_frame, text="", font=("Arial", 10, "bold"), anchor="center")

        self.start_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.choose_image_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.clear_image_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.clear_points_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.change_color_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.show_nums_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.start_new_iteration_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.checkbutton.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.label1.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.start_auto_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.stop_auto_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.iteration_text.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.feromone_label.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.num_of_options_text.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.num_of_options.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=1)

        self.ax.spines['top'].set_linewidth(0)
        self.ax.spines['right'].set_linewidth(0)
        self.ax.spines['bottom'].set_linewidth(0)
        self.ax.spines['left'].set_linewidth(0)
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)

    def on_click(self, event):
        lang = language_dict[self.current_language]
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            self.show_error_message('Ви вийшли за межі', 1)
            return

        button = event.button
        if button == 1:
            self.handle_left_click(x, y, lang)
        elif button == 3:
            self.handle_right_click(x, y, lang)

    def handle_left_click(self, x, y, lang):
        too_close = any(math.sqrt((x-px)**2 + (y-py)**2) < self.threshold_distance for px, py in self.points)
        if not too_close:
            if self.show_nums and len(self.points) + 1 > 40:
                self.show_error_message('Для оптимізації вимкніть нумерацію')
            else:
                self.points.append((x, y))
                self.update_optins()
                self.ax.scatter(*zip(*self.points), s=120, c=self.dot_color)
                self.update_point_labels(text_color=self.text_color)
                if self.img_array is not None:
                    self.ax.imshow(self.img_array, extent=[0, 10, 0, 10])
                self.canvas.draw()
        else:
            self.show_error_message('Надто близько', 1)

    def handle_right_click(self, x, y, lang):
        if len(self.points) == 0:
            self.show_error_message('Немає точок', 1)
        else:
            for idx, (px, py) in enumerate(self.points):
                if math.sqrt((x-px)**2 + (y-py)**2) < self.threshold_distance:
                    if len(self.points) == 1:
                        self.clear_points()
                    else:
                        self.points.pop(idx)
                        self.update_optins()
                        self.reload_graph()
                    break

    def prepare(self):
        self.G = nx.Graph()
        self.G.add_nodes_from(self.points)

        for i in range(len(self.points)):
            for j in range(i+1, len(self.points)):
                distance = math.sqrt((self.points[i][0] - self.points[j][0]) ** 2 + (self.points[i][1] - self.points[j][1]) ** 2)
                self.distances[(i, j)] = distance / 10
                self.feromons[(i, j)] = standart_feromon
                self.G.add_edge(self.points[i], self.points[j])

        if self.debugging:
            print("Відстані:", self.distances)
            for i, node in enumerate(self.G.nodes()):
                print(f"Вузол: №{i}", node)

        self.ants = len(self.points)

    def start_algor(self):
        if len(self.points) < 2:
            self.show_error_message('Замало точок', 1)
        else:
            self.iteration = 0
            self.feromons = {}
            self.routes = {}
            self.prepare()
            self.update_edges()
            self.stop_auto()

    def get_edges_from_routes(self, num):
        edges = set()
        route = list(self.routes.values())[num]
        for i in range(len(route) - 1):
            edge = (min(route[i], route[i + 1]), max(route[i], route[i + 1]))
            edges.add(edge)
        return edges

    def ant_colony(self):
        if self.iteration is None:
            self.show_error_message('Почніть алгоритм', 1)
            self.stop_auto()
            return

        self.iteration += 1
        self.routes = {}
        total_distances = []

        for ant in range(self.ants):
            total_distance = 0
            unvisited_cities = set(range(len(self.points)))

            if self.is_random:
                current_city = random.choice(list(unvisited_cities))
            else:
                current_city = ant

            unvisited_cities.remove(current_city)
            route = [current_city]

            while unvisited_cities:
                probabilities = self.calculate_probability(current_city, unvisited_cities)
                next_city = random.choices(list(probabilities.keys()), list(probabilities.values()), k=1)[0]
                total_distance += self.distances.get((min(current_city, next_city), max(current_city, next_city)), 0)
                route.append(next_city)
                unvisited_cities.remove(next_city)
                current_city = next_city

            route.append(route[0])
            total_distance += self.distances.get((min(route[-2], route[0]), max(route[-2], route[0])), 0)

            self.routes[ant] = route
            total_distances.append(total_distance)

        for k, route in enumerate(self.routes.values()):
            for i in range(len(route) - 1):
                edge = (min(route[i], route[i + 1]), max(route[i], route[i + 1]))
                self.feromons[edge] = (Q * total_distances[k]) + (self.feromons[edge] * PUC)

            self.evaporate_pheromones(k)

        self.update_edges()

        total_feromone_length = sum(self.distances[edge] * 10 for edge, feromone in self.feromons.items() if feromone > 1)
        lang = language_dict[self.current_language]
        if self.iteration >= 5:
            self.feromone_label.config(text=f"{lang['length']} {total_feromone_length:.2f}")
        else:
            self.feromone_label.config(text=lang['length'])

    def calculate_probability(self, ant, unvisited_cities):
        total = 0
        probabilities = {}

        for city in unvisited_cities:
            distance = self.distances.get((ant, city), self.distances.get((city, ant)))
            feromon = self.feromons.get((ant, city), self.feromons.get((city, ant)))
            total += (feromon ** ALPHA) * ((1 / distance) ** BETA)

        for city in unvisited_cities:
            distance = self.distances.get((ant, city), self.distances.get((city, ant)))
            feromon = self.feromons.get((ant, city), self.feromons.get((city, ant)))
            probabilities[city] = ((feromon ** ALPHA) * ((1 / distance) ** BETA)) / total

        return probabilities

    def evaporate_pheromones(self, num):
        for edge in self.feromons.keys():
            if edge not in self.get_edges_from_routes(num):
                self.feromons[edge] *= PUC

    def update_edges(self):
        if not self.feromons:
            return

        def all_values_equal_to(dictionary, value):
            return all(v == value for v in dictionary.values())

        self.reload_graph()
        pos = {node: node for node in self.G.nodes()}
        widths = [edge_feromon / 10 for edge_feromon in self.feromons.values()] if not all_values_equal_to(self.feromons, 0.2) else [edge_feromon for edge_feromon in self.feromons.values()]
        alphas = [1 - min(edge_feromon / max(self.feromons.values()), 0.9) for edge_feromon in self.feromons.values()]
        nx.draw_networkx_nodes(self.G, pos=pos, ax=self.ax, node_color=self.dot_color, node_size=120)
        alpha_inverted = [1 - alpha for alpha in alphas]
        nx.draw_networkx_edges(self.G, pos=pos, ax=self.ax, edge_color='green', width=widths, alpha=alpha_inverted)
        self.update_point_labels(text_color=self.text_color)
        if self.iteration is not None:
            lang = language_dict[self.current_language]
            self.iteration_text.config(text=f'{lang['iterations']} {self.iteration}')
        self.canvas.draw()

    def exit_program(self):
        self.window.destroy()

    def show_error_message(self, message, type=0):
        dur = 3000 if type == 0 else 1000
        toast = ToastNotification(
            title="Помилка!" if self.current_language == 'uk' else "Error!",
            message=message if self.current_language == 'uk' else errors_dict[message],
            duration=dur,
            icon=' ⚠'
        )
        toast.show_toast()

    def choose_image(self):
        try:
            file_path = filedialog.askopenfilename()
            self.clear_image(a=1)
            img = Image.open(file_path)
            self.img_array = np.array(img)
            self.ax.imshow(self.img_array, extent=[0, 10, 0, 10])
            self.update_point_labels(text_color=self.text_color)
            self.canvas.draw()
        except:
            self.show_error_message('Оберіть картинку')

    def clear_image(self, a=0):
        if self.img_array is None:
            if a == 0:
                self.show_error_message('Немає фону', 1)
                return
        else:
            self.img_array = None
            for img in self.ax.images:
                img.remove()
            self.canvas.draw()

    def clear_points(self):
        self.iteration = None
        self.iteration_text.config(text='Кількість ітерацій:')
        self.feromone_label.config(text="Довжина:")
        self.feromons = {}
        self.stop_auto()

        if len(self.points) == 0:
            self.show_error_message('Немає точок', 1)
        else:
            self.points = []
            self.ax.cla()
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(0, 10)
            if self.img_array is not None:
                self.ax.imshow(self.img_array, extent=[0, 10, 0, 10])
            self.canvas.draw()

        self.update_optins()

    def change_dot_color(self):
        if len(self.points) == 0:
            self.show_error_message('Немає точок', 1)
        else:
            self.dot_color, self.text_color = ('white', 'black') if self.dot_color == 'black' else ('black', 'white')
            self.reload_graph()
            self.update_edges()

    def update_point_labels(self, text_color=None):
        for label in self.point_labels:
            label.set_visible(False)
        self.point_labels = []

        if self.show_nums:
            for i, (px, py) in enumerate(self.points):
                label = self.ax.annotate(f'{i}', (px, py), textcoords="offset points", xytext=(0, -3), ha='center', color=text_color, fontsize=6)
                self.point_labels.append(label)
            self.canvas.draw()

    def reload_graph(self):
        self.ax.cla()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.scatter(*zip(*self.points), s=120, c=self.dot_color)
        self.update_point_labels(text_color=self.text_color)
        if self.img_array is not None:
            self.ax.imshow(self.img_array, extent=[0, 10, 0, 10])
        self.canvas.draw()

    def start_auto(self):
        if self.iteration is None:
            self.start_algor()

        self.stop_auto_iteration = False
        thread = threading.Thread(target=self.auto_iteration)
        thread.start()

    def stop_auto(self):
        self.stop_auto_iteration = True

    def auto_iteration(self):
        try:
            while not self.stop_auto_iteration:
                self.ant_colony()
                time.sleep(0.3)
        except:
            pass

    def update_optins(self):
        summa = 1
        if len(self.points) > 0:
            for i in range(1, len(self.points)):
                summa *= i
        else:
            summa = 0

        summa = int(summa) / 2

        if len(str(summa)) > 15:
            power = len(str(summa)) - 15
            summa_txt = str(summa)[:15] + " * 10^" + str(power)
            self.num_of_options.config(text=summa_txt)
        else:
            self.num_of_options.config(text=summa)

    def handle_check_button(self):
        self.is_random = self.selected_var.get() == 1

    def unshow_nums(self):
        if len(self.points) == 0:
            self.show_error_message('Немає точок', 1)
            return
        self.show_nums = not self.show_nums
        self.show_nums_button.config(text="Приховати номери" if self.current_language == 'uk' else "Hide Numbers" if self.show_nums else "Показати номери" if self.current_language == 'uk' else "Show Numbers")
        self.reload_graph()
        self.update_edges()
        self.update_point_labels()

    def update_ui_language(self):
        lang = language_dict[self.current_language]
        self.start_button.config(text=lang['start'])
        self.choose_image_button.config(text=lang['choose_image'])
        self.clear_image_button.config(text=lang['clear_image'])
        self.clear_points_button.config(text=lang['clear_points'])
        self.change_color_button.config(text=lang['change_color'])
        self.show_nums_button.config(text=lang['show_nums'])
        self.start_new_iteration_button.config(text=lang['start_new_iteration'])
        self.checkbutton.config(text=lang['random_city'])
        self.label1.config(text=lang['auto'])
        self.start_auto_button.config(text=lang['start_auto'])
        self.stop_auto_button.config(text=lang['stop_auto'])
        self.iteration_text.config(text=lang['iterations'])
        self.feromone_label.config(text=lang['length'])
        self.num_of_options_text.config(text=lang['options'])
        self.menu_frame.config(text=lang['menu'])

    def switch_language(self):
        self.current_language = 'en' if self.current_language == 'uk' else 'uk'
        self.update_ui_language()

if __name__ == "__main__":
    root = ttk.Window(themename='superhero')
    app = AntColonyApp(root)
    root.mainloop()
