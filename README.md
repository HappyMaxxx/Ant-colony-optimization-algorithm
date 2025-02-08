# Ant Colony Algorithm Visualization

This project is an implementation and visualization of the Ant Colony Optimization (ACO)
algorithm for solving the Traveling Salesman Problem (TSP). The
application allows users to interactively place points (cities) on a canvas, run the
ACO algorithm, and visualize the pheromone-based pathfinding process.

---

## Features  

- **Interactive GUI:** Built using Tkinter and ttkbootstrap.
- **Graph Representation:** Uses NetworkX to manage the graph structure.
- **Algorithm Visualization:** Displays pheromone trails and optimal paths dynamically.
- **Image Support:** Allows adding background images for visualization.
- **Auto Iteration:** Supports continuous execution of the ACO algorithm.
- **Customizable Settings:** Users can change colors, toggle number labels, and adjust parameters.
- **Multilingual Support:** English and Ukrainian languages available.

---

## Installation

Create and activate a Python virtual environment:  

```bash
python3 -m venv venv
source venv/bin/activate  # For Linux and macOS
# or
venv\Scripts\activate     # For Windows
```
---

Install the required dependencies from `requirements.txt`:  

```bash
pip install -r requirements.txt
```

## Usage

Run the application using:

```bash
python main.py
```

---

### Controls 

- **Left Click:** Add a city (point) to the graph.
- **Right Click:** Remove a city.
- **Start Algorithm:** Initializes the graph and pheromone levels.
- **Run Iteration:** Executes one step of the ACO algorithm.
- **Auto Run:** Continuously runs iterations.
- **Choose Image:** Adds a background image.
- **Clear Points:** Resets the graph.
- **Change Color:** Switches between black and white nodes.
- **Show/Hide Numbers:** Toggles numbering on points.

---

### Algorithm Overview

The Ant Colony Optimization (ACO) algorithm is inspired by the foraging behavior of ants. Key steps include:

1. Initialization: Cities are defined as nodes in a graph.
2. Ant Movement: Each ant probabilistically chooses the next city based on pheromone levels and distance.
3. Pheromone Update: Trails are reinforced based on the quality of the path taken.
4. Evaporation: Pheromone levels decay over time to avoid stagnation.
5. Iteration: Steps 2-4 repeat to find an optimal path.

---

### Parameters

- **Alpha (α):** Controls the influence of pheromones.
- **Beta (β):** Controls the influence of distance.
- **Evaporation Rate:** Defines pheromone decay over iterations.
- **Pheromone Constant (Q):** Determines pheromone reinforcement.

---

### Author

Developed as a course project in the discipline “Algorithmization and Programming” in the first year of study of the specialty 122 “Computer Science” at VNTU.
