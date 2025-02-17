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

debugging = False
show_nums = True

fig = plt.Figure(figsize=(7, 5))
ax = fig.add_subplot(111)
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

window = ttk.Window(themename='superhero')
canvas = FigureCanvasTkAgg(fig, master=window)
window.title("Ant Colony")
canvas.draw()

frame = ttk.Frame(window)
frame.pack(side=ttk.RIGHT, fill=ttk.BOTH, expand=False)

points = []
dot_color: str = 'black'
text_color: str = 'white'

threshold_distance = 0.5
img_array = None

text_for_error: str = ''

point_labels = []

def on_click(event):
    global iteration

    lang = language_dict[current_language]

    x = event.xdata
    y = event.ydata
    if x is None or y is None:
        show_error_message('Ви вийшли за межі', 1)
        return

    button = event.button
    if button == 1:
        too_close = False

        iteration = None
        iteration_text.config(text=lang['iterations'])
        feromone_label.config(text=lang['length'])
        stop_auto()

        for px, py in points:
            distance = math.sqrt((x-px)**2 + (y-py)**2)
            if distance < threshold_distance:
                too_close = True
                break

        if not too_close:
            if show_nums and len(points)+1 > 40:
                show_error_message('Для оптимізації вимкніть нумерацію')
                
            points.append((x, y))
            update_optins()
            ax.scatter(*zip(*points), s=120, c=dot_color)
            update_point_labels(text_color=text_color)
            if img_array is not None:
                ax.imshow(img_array, extent=[0, 10, 0, 10])
            canvas.draw()
        else:
            show_error_message('Надто близько', 1)

    elif button == 3:

        iteration = None
        iteration_text.config(text=lang['iterations'])
        feromone_label.config(text=lang['length'])
        stop_auto()

        if len(points)-1 == -1:
            show_error_message('Немає точок', 1)
        else:
            for idx, (px, py) in enumerate(points):
                distance = math.sqrt((x-px)**2 + (y-py)**2)
                if distance < threshold_distance:
                    if len(points)-1 == 0:
                        clear_points()
                        return
                    points.pop(idx)
                    update_optins()
                    reload_graph()
                    break

distances = {}
feromons = {}
routes = {}
iteration = None

def prepare():
    global G, distances, feromons, ants

    G = nx.Graph()
    G.add_nodes_from(points)

    for i in range(len(points)):
        for j in range(i+1, len(points)):
            distance = math.sqrt((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2)
            distances[(i, j)] = distance/10
            feromons[(i, j)] = standart_feromon
            G.add_edge(points[i], points[j])
    
    if debugging:
        print("Відстані:", distances)
        for i, node in enumerate(G.nodes()):
            print(f"Вузол: №{i}", node)
        
    ants = len(points)

def start_algor():
    global distances, feromons, iteration, routes

    if len(points) < 2:
        show_error_message('Замало точок', 1)
        return
    else:
        iteration = 0
        feromons = {}
        routes = {}
        prepare()
        update_edges()
        stop_auto()

def get_edges_from_routes(num):
    edges = set()
    route = list(routes.values())[num]
    for i in range(len(route)-1):
        edge = (min(route[i], route[i+1]), max(route[i], route[i+1]))
        edges.add(edge)
    return edges

def ant_colony():
    global G, distances, feromons, iteration, ants, routes
    
    if debugging:
        start = time.time()

    if iteration is None:
        show_error_message('Почніть алгоритм', 1)
        stop_auto()
        return

    iteration += 1
    routes = {}
    total_distances = []

    for ant in range(ants):
        total_distance = 0
        unvisited_cities = set(range(len(points)))

        if is_random: current_city = random.choice(list(unvisited_cities))
        else: current_city = ant

        unvisited_cities.remove(current_city)
        route = [current_city]

        while unvisited_cities:
            probabilities = calculate_probability(current_city, unvisited_cities)
            if debugging:
                print(probabilities)
            keyses = list(probabilities.keys())
            values = list(probabilities.values())
            if sum(values) == 0:
                pass
            next_city = random.choices(keyses, values, k=1)[0]
            if current_city < next_city:
                total_distance += distances[(current_city, next_city)]
            else:
                total_distance += distances[(next_city, current_city)]
            route.append(next_city)
            unvisited_cities.remove(next_city)
            current_city = next_city

        route.append(route[0])
        if route[len(route)-2] < route[0]:
            total_distance += distances[(route[len(route)-2], route[0])]
        else:
            total_distance += distances[(route[0], route[len(route)-2])]

        routes[ant] = route
        total_distances.append(total_distance)

    for k, route in enumerate(routes.values()):
        if debugging:
            print("Мурашка", k, "пройшла маршрут", route)
        for i in range(len(route)-1):
            if (route[i] < route[i+1]):
                if debugging:
                    print("Пройшли через:", (route[i], route[i+1]))
                feromons[(route[i], route[i+1])] = (Q * total_distances[k]) + (feromons[(route[i], route[i+1])] * PUC)
            else:
                if debugging:
                    print("Пройшли через обернена:", (route[i], route[i+1]))
                feromons[(route[i+1], route[i])] = (Q * total_distances[k]) + (feromons[(route[i+1], route[i])] * PUC)

        evaporate_pheromones(k)

    if debugging:
        print(feromons)
    update_edges()

    total_feromone_length = 0
    for edge, feromone in feromons.items():
        if feromone > 1:
            total_feromone_length += distances[edge]*10

    lang = language_dict[current_language]
    if iteration >= 5:
        feromone_label.config(text=f"{lang['length']} {total_feromone_length:.2f}")
    else:
        feromone_label.config(text=lang['length'])

    if debugging:
        print(f"Час виконання ітерації {iteration}:", time.time()-start, f'Для кількості мітст: {ants}')

def calculate_probability(ant, unvisited_cities):
    total = 0
    probabilities = {}

    for city in unvisited_cities:
        distance = distances.get((ant, city), distances.get((city, ant)))
        feromon = feromons.get((ant, city), feromons.get((city, ant)))
        total += (feromon ** ALPHA) * ((1 / distance) ** BETA)

    for city in unvisited_cities:
        distance = distances.get((ant, city), distances.get((city, ant)))
        feromon = feromons.get((ant, city), feromons.get((city, ant)))
        probabilities[city] = ((feromon ** ALPHA) * ((1 / distance) ** BETA)) / total

    return probabilities

def evaporate_pheromones(num):
    global feromons, routes, distances

    for edge in feromons.keys():
        if edge not in get_edges_from_routes(num):
            if debugging:
                print("Не пройшли:", edge)
            feromons[edge] *= PUC

def update_edges():
    if feromons == {}:
        return

    def all_values_equal_to(dictionary, value):
        for v in dictionary.values():
            if v != value:
                return False
        return True

    reload_graph()
    pos = {node: node for node in G.nodes()}
    if all_values_equal_to(feromons, 0.2):
        widths = [edge_feromon for edge_feromon in feromons.values()]
    else:
        widths = [edge_feromon/10 for edge_feromon in feromons.values()]
    alphas = [1 - min(edge_feromon / max(feromons.values()), 0.9) for edge_feromon in feromons.values()]
    nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color=dot_color, node_size=120)
    alpha_inverted = [1 - alpha for alpha in alphas]
    nx.draw_networkx_edges(G, pos=pos, ax=ax, edge_color='green', width=widths, alpha=alpha_inverted)
    update_point_labels(text_color=text_color)
    if iteration is not None:
        lang = language_dict[current_language]
        iteration_text.config(text=f'{lang['iterations']} {iteration}')
    canvas.draw()

def exit_program():
    window.destroy()

def show_error_message(message, type = 0):
    global text_for_error

    if type == 0:
        dur = 3000
    else:
        dur = 1000

    toast = ToastNotification(
        title = "Помилка!" if current_language == 'uk' else "Error!",
        message = message if current_language == 'uk' else errors_dict[message],
        duration = dur,
        icon=' ⚠'
    )

    toast.show_toast()

def choose_image():
    global img_array

    try:
        file_path = filedialog.askopenfilename()
        clear_image(a=1)
        img = Image.open(file_path)
        img_array = np.array(img)
        ax.imshow(img_array, extent=[0, 10, 0, 10])
        update_point_labels(text_color=text_color)
        canvas.draw()
    except:
        show_error_message('Оберіть картинку')

def clear_image(a=0):
    global img_array

    if img_array is None:
        if a == 0:
            show_error_message('Немає фону', 1)
            return
        else:
            pass
    else:
        img_array = None
        for img in ax.images:
            img.remove()
        canvas.draw()

def clear_points():
    global points, iteration, feromons

    iteration = None
    iteration_text.config(text='Кількість ітерацій:')
    feromone_label.config(text="Довжина:")
    feromons = {}
    stop_auto()

    if len(points) == 0:
        show_error_message('Немає точок', 1)
        return
    else:
        points = []

        ax.cla()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        if img_array is not None:
            ax.imshow(img_array, extent=[0, 10, 0, 10])
        canvas.draw()

    update_optins()

def change_dot_color():
    global dot_color, text_color

    if len(points) == 0:
        show_error_message('Немає точок', 1)
        return
    else:
        if dot_color == 'white':
            dot_color = 'black'
            text_color = 'white'
        else:
            dot_color = 'white'
            text_color = 'black'

        reload_graph()
        update_edges()
        return

def update_point_labels(text_color=text_color):
    global point_labels
    for label in point_labels:
        label.set_visible(False) 
    point_labels = []
    
    if show_nums:
        for i, (px, py) in enumerate(points):
            label = ax.annotate(f'{i}', (px, py), textcoords="offset points", xytext=(0,-3), ha='center', color=text_color, fontsize=6)
            point_labels.append(label)
        canvas.draw()

def reload_graph():
    ax.cla()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.scatter(*zip(*points), s=120, c=dot_color)
    update_point_labels(text_color=text_color)
    if img_array is not None:
        ax.imshow(img_array, extent=[0, 10, 0, 10])
    canvas.draw()

stop_auto_iteration = False

def start_auto() -> None:
    global stop_auto_iteration

    if iteration is None:
        start_algor()

    stop_auto_iteration = False
    thread = threading.Thread(target=auto_iteration)
    thread.start()

def stop_auto() -> None:
    global stop_auto_iteration, clear

    clear = True
    stop_auto_iteration = True

def auto_iteration():
    global clear

    clear = False
    try:

        while not stop_auto_iteration:
            ant_colony()
            time.sleep(0.3)
    except:
        pass

def update_optins():
    summa = 1

    if len(points) > 0:
        for i in range(1, len(points)):
            summa *= i
    else:
        summa = 0

    summa = int(summa) /  2

    if len(str(summa)) > 15:
        power = len(str(summa))-15
        summa_txt = str(summa)[:15] + " * 10^" + str(power)
        num_of_options.config(text=summa_txt)
    else:
        num_of_options.config(text=summa)

selected_var = IntVar(value=0)
is_random = False

def handle_check_button():
    global is_random
    if selected_var.get() == 1: is_random = True
    else: is_random = False

def unshow_nums():
    global show_nums

    if len(points) == 0:
        show_error_message('Немає точок', 1)
        return
    show_nums = False if show_nums else True
    if show_nums:
        show_nums_button.config(text="Приховати номери" if current_language == 'uk' else "Hide Numbers")
    else:
        show_nums_button.config(text="Показати номери" if current_language == 'uk' else "Show Numbers")

    reload_graph()
    update_edges()
    update_point_labels()

def update_ui_language():
    lang = language_dict[current_language]
    start_button.config(text=lang['start'])
    choose_image_button.config(text=lang['choose_image'])
    clear_image_button.config(text=lang['clear_image'])
    clear_points_button.config(text=lang['clear_points'])
    change_color_button.config(text=lang['change_color'])
    show_nums_button.config(text=lang['show_nums'])
    start_new_iteration_button.config(text=lang['start_new_iteration'])
    checkbutton.config(text=lang['random_city'])
    label1.config(text=lang['auto'])
    start_auto_button.config(text=lang['start_auto'])
    stop_auto_button.config(text=lang['stop_auto'])
    iteration_text.config(text=lang['iterations'])
    feromone_label.config(text=lang['length'])
    num_of_options_text.config(text=lang['options'])
    menu_frame.config(text=lang['menu'])

def switch_language():
    global current_language
    current_language = 'en' if current_language == 'uk' else 'uk'
    update_ui_language()

canvas.get_tk_widget().pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True, padx=10, pady=15)

menu_frame = Labelframe(frame, padding="10")
menu_frame.pack(fill="both", expand="yes", padx=10, pady=(3, 15))

menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

language_menu = tk.Menu(menu_bar, tearoff=0)
language_menu.add_command(label="Switch Language", command=switch_language)
menu_bar.add_cascade(label="Language", menu=language_menu)

start_button = ttk.Button(menu_frame, command=start_algor)
choose_image_button = ttk.Button(menu_frame, command=choose_image)
clear_image_button = ttk.Button(menu_frame, command=clear_image)
clear_points_button = ttk.Button(menu_frame, command=clear_points)
change_color_button = ttk.Button(menu_frame, command=change_dot_color)
show_nums_button = ttk.Button(menu_frame, command=unshow_nums)
start_new_iteration_button = ttk.Button(menu_frame, command=ant_colony)
checkbutton = ttk.Checkbutton(menu_frame, variable=selected_var, onvalue=1, offvalue=0, command=handle_check_button)
label1 = tk.Label(menu_frame, font=("Arial", 10, "bold"))
start_auto_button = ttk.Button(menu_frame, command=start_auto)
stop_auto_button = ttk.Button(menu_frame, command=stop_auto)
iteration_text = tk.Label(menu_frame, font=("Arial", 10, "bold"))
feromone_label = tk.Label(menu_frame, font=("Arial", 10, "bold"))
num_of_options_text = tk.Label(menu_frame, font=("Arial", 10, "bold"))
num_of_options = ttk.Label(menu_frame, text="", font=("Arial", 10, "bold"), anchor="center")

start_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
choose_image_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
clear_image_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
clear_points_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
change_color_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
show_nums_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
start_new_iteration_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
checkbutton.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
label1.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
start_auto_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
stop_auto_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
iteration_text.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
feromone_label.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
num_of_options_text.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
num_of_options.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=1)

ax.spines['top'].set_linewidth(0)
ax.spines['right'].set_linewidth(0)
ax.spines['bottom'].set_linewidth(0)
ax.spines['left'].set_linewidth(0)
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)

cid = canvas.mpl_connect('button_press_event', on_click)

update_ui_language()
window.mainloop()