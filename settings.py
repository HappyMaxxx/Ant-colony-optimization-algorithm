standart_feromon: float = 0.2 # Початкове значення феромону на шляхах (Initial pheromone value on paths)
ALPHA: int = 1
BETA: int = 3
PUC: float = 0.64 # Коефіцієнт оновлення шляху (Pheromone update coefficient)
Q: int = 4

current_language = 'en'

language_dict = {
    'uk': {
        'start': 'Підготувати',
        'choose_image': 'Обрати картину для фону',
        'clear_image': 'Очистити фон',
        'clear_points': 'Очистити точки',
        'change_color': 'Змінити колір крапочок',
        'show_nums': 'Приховати номери',
        'start_new_iteration': 'Почати нову ітерацію',
        'random_city': 'Випадкове місто',
        'auto': 'Автоматично',
        'start_auto': 'Почати',
        'stop_auto': 'Зупинити',
        'iterations': 'Кількість ітерацій:',
        'length': 'Довжина:',
        'options': 'Кількість варіантів шляху:',
        'menu': 'Меню',
    },
    'en': {
        'start': 'Prepare',
        'choose_image': 'Choose Image for Background',
        'clear_image': 'Clear Background',
        'clear_points': 'Clear Points',
        'change_color': 'Change Dot Color',
        'show_nums': 'Hide Numbers',
        'start_new_iteration': 'Start New Iteration',
        'random_city': 'Random City',
        'auto': 'Automatic',
        'start_auto': 'Start',
        'stop_auto': 'Stop',
        'iterations': 'Number of Iterations:',
        'length': 'Length:',
        'options': 'Number of Path Options:',
        'menu': 'Menu',
    }
}

errors_dict = {
    'Ви вийшли за межі': 'You are out of bounds',
    'Для оптимізації вимкніть нумерацію': 'To optimize, turn off numbering',
    'Надто близько': 'Too close',
    'Немає точок': 'No points',
    'Замало точок': 'Not enough points',
    'Почніть алгоритм': 'Start the algorithm',
    'Оберіть картинку': 'Choose a picture',
    'Немає фону': 'No background',

}