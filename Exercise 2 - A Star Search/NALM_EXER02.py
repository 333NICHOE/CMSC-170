'''
CMSC 170: Introduction to Artificial Intelligence
Exercise 2: Solving the 8-Puzzle Game using A*

Nico Antonio L. Montero
2021-68215
CMSC 170 GH6L
'''
from collections import deque
import tkinter as tk
from tkinter import filedialog, messagebox
import heapq
import time 
from memory_profiler import profile


class Node:
    def __init__(self, state, empty_tile, action=None, parent=None, path_cost=0, fn=0, gn=0, hn=0):
        self.state = state
        self.empty_tile = empty_tile
        self.action = action
        self.parent = parent
        self.path_cost = path_cost
        self.fn = fn
        self.gn = gn
        self.hn = hn
    
    def __lt__(self, other):
        return self.path_cost < other.path_cost

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Game")
        self.goal_tiles = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        self.initial_node = None  # Will store the initial node of the puzzle
        self.saved_node = None    # Will store the saved initial state as a Node
        self.create_widgets()
        self.initialize_game()

    # -----------------------------------------------------------------------------------------
    # Rendering the elements in the GUI
    # -----------------------------------------------------------------------------------------
    def create_widgets(self):
        header_frame = tk.Frame(self.root)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(header_frame, text="8-Puzzle Game", font=('Helvetica', 20, 'bold'))
        title_label.pack()
        
        course_label = tk.Label(header_frame, text="CMSC 170", font=('Helvetica', 14))
        course_label.pack()
        
        # CHANGE TO YOUR NAME
        author_label = tk.Label(header_frame, text="Nico Antonio L. Montero", font=('Helvetica', 14))
        author_label.pack()

        self.time_label = tk.Label(self.root, text="Time Taken: 0.0000 ns", font=('Helvetica', 14))
        self.time_label.pack()
        
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg='white', borderwidth=0, highlightthickness=0, relief=tk.SOLID)
        self.canvas.pack(side=tk.TOP, padx=(2,0), pady=(2,0))
        self.canvas.bind("<Button-1>", self.click)

        self.import_button = tk.Button(self.root, text="Import Configuration", command=self.import_configuration)
        self.import_button.pack(side=tk.TOP, padx=10, pady=5)

        self.method_var = tk.StringVar(value="BFS")
        self.heuristic_var = tk.StringVar(value="Manhattan Distance")

        self.method_frame = tk.Frame(self.root)
        self.method_frame.pack(side=tk.TOP, padx=10, pady=5)
        
        self.bfs_rb = tk.Radiobutton(self.method_frame, text="BFS", variable=self.method_var, value="BFS")
        self.bfs_rb.pack(side=tk.LEFT)
        self.dfs_rb = tk.Radiobutton(self.method_frame, text="DFS", variable=self.method_var, value="DFS")
        self.dfs_rb.pack(side=tk.LEFT)
        self.astar_rb = tk.Radiobutton(self.method_frame, text="A*", variable=self.method_var, value="A*")
        self.astar_rb.pack(side=tk.LEFT)

        self.heuristic_menu = tk.OptionMenu(self.method_frame, self.heuristic_var, "Misplaced Tiles", "Manhattan Distance", "Adjacent Tiles")
        self.heuristic_menu.pack(side=tk.LEFT, padx=5)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.TOP, padx=10, pady=5)

        self.solve_button = tk.Button(self.button_frame, text="Solve", command=self.solve_puzzle)
        self.solve_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_puzzle)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

        self.solution_label = tk.Label(self.text_frame, text="Puzzle is Solvable", font=('Helvetica', 14, 'bold'))
        self.solution_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.scrollbar = tk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.directions_text = tk.Text(self.text_frame, height=3, width=40, yscrollcommand=self.scrollbar.set, wrap=tk.WORD, font=('Helvetica', 16))
        self.directions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.directions_text.yview)
        self.directions_text.config(state=tk.DISABLED)

    # -----------------------------------------------------------------------------------------
    # Initializes the game; default initial state is set here
    # -----------------------------------------------------------------------------------------
    def initialize_game(self):
        default_initial_tiles = [
            [2, 3, 0],
            [1, 5, 6],
            [4, 7, 8]
        ]
        self.initial_node = Node(default_initial_tiles, self.find_empty_spot(default_initial_tiles))
        self.saved_node = Node([row[:] for row in default_initial_tiles], self.find_empty_spot(default_initial_tiles))
        self.load_tiles(self.initial_node.state)
        self.check_solvability(self.initial_node.state)

    # -----------------------------------------------------------------------------------------
    # Finding the empty tile
    # @params:
    #	tiles - puzzle state
    # -----------------------------------------------------------------------------------------
    def find_empty_spot(self, tiles):
        return next((i, j) for i, row in enumerate(tiles) for j, tile in enumerate(row) if tile == 0)

    # -----------------------------------------------------------------------------------------
    # Loads the current state by drawing the elements in the GUI
    # @params:
    #	tiles - puzzle state
    # -----------------------------------------------------------------------------------------
    def load_tiles(self, tiles):
        self.draw_tiles(tiles)

    # -----------------------------------------------------------------------------------------
    # Updates the game board given the current state
    # @params:
    #	tiles - puzzle state
    # -----------------------------------------------------------------------------------------
    def draw_tiles(self, tiles):
        self.canvas.delete("all")
        for i, row in enumerate(tiles):
            for j, tile in enumerate(row):
                if tile != 0:
                    x0, y0 = j * 100, i * 100
                    x1, y1 = x0 + 100, y0 + 100
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill='#3566d5', activefill="#2d55b1", width=2)
                    self.canvas.create_text((x0 + 50, y0 + 50), text=str(tile), font=('Helvetica', 24), fill='white')

    # -----------------------------------------------------------------------------------------
    # Performs swapping of the tiles when an event (click) is detected
    # @params:
    #	event - triggers (e.g., mouse click)
    # -----------------------------------------------------------------------------------------
    def click(self, event):
        col, row = event.x // 100, event.y // 100
        if self.is_adjacent((row, col), self.initial_node.empty_tile):
            self.swap_tiles(self.initial_node.state, (row, col), self.initial_node.empty_tile)
            self.initial_node.empty_tile = (row, col)
            self.draw_tiles(self.initial_node.state)
            if self.check_victory():
                messagebox.showinfo("8-Puzzle", "Congratulations! You solved the puzzle!")

    # -----------------------------------------------------------------------------------------
    # Checks adjacency to make sure swapping of tile is valid
    # @params:
    #	pos1 - tuple of x,y coordinates of the clicked tile
    #   pos2 - tuple of x,y coordinates of the empty tile
    # -----------------------------------------------------------------------------------------
    def is_adjacent(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    # -----------------------------------------------------------------------------------------
    # Swaps tiles given the position
    # @params:
    #	tiles - puzzle state
    #	pos1 - tuple of x,y coordinates of the clicked tile
    #   pos2 - tuple of x,y coordinates of the empty tile
    # -----------------------------------------------------------------------------------------
    def swap_tiles(self, tiles, pos1, pos2):
        tiles[pos1[0]][pos1[1]], tiles[pos2[0]][pos2[1]] = tiles[pos2[0]][pos2[1]], tiles[pos1[0]][pos1[1]]

    # -----------------------------------------------------------------------------------------
    # Check if the player has won
    # -----------------------------------------------------------------------------------------
    def check_victory(self):
        return self.initial_node.state == self.goal_tiles
    
    # -----------------------------------------------------------------------------------------
    # Makes sure that the imported file is a valid puzzle configuration
    # @params:
    #	tiles - puzzle state
    # -----------------------------------------------------------------------------------------
    def validate_tiles(self, tiles):
        flattened = [num for row in tiles for num in row]
        return sorted(flattened) == list(range(9))

    # -----------------------------------------------------------------------------------------
    # Resets the puzzle to its initial state
    # -----------------------------------------------------------------------------------------
    def reset_puzzle(self):
        self.initial_node = Node([row[:] for row in self.saved_node.state], self.saved_node.empty_tile)
        self.load_tiles(self.initial_node.state)
        self.check_solvability(self.initial_node.state)
        self.clear_directions()
        self.time_label.config( text="Time Taken: 0.0000 ns", font=('Helvetica', 14))


    # -----------------------------------------------------------------------------------------
    # Clears the directions rendered in the GUI
    # -----------------------------------------------------------------------------------------
    def clear_directions(self):
        self.directions_text.config(state=tk.NORMAL)
        self.directions_text.delete('1.0', tk.END)
        self.directions_text.config(state=tk.DISABLED)

    # -----------------------------------------------------------------------------------------
    # Animation of the given solution
    # @params
    #   solution - list of states from the initial to the goal state
    #   directions - list of actions taken from initial to goal state
    # -----------------------------------------------------------------------------------------
    def animate_solution(self, solution, directions):
        for state, direction in zip(solution, directions):
            self.directions_text.config(state=tk.NORMAL)
            self.directions_text.insert(tk.END, direction + " ")
            self.directions_text.config(state=tk.DISABLED)
            self.draw_tiles(state)
            self.root.update()
            self.root.after(500)
        self.draw_tiles(solution[-1])
    
    # -----------------------------------------------------------------------------------------
    # Lets the user choose an AI agent and animates the given solution
    # -----------------------------------------------------------------------------------------
    def solve_puzzle(self):
        self.solution_label.config(text="Solving...")
        self.root.update()

        search_method = self.method_var.get()
        heuristic = self.heuristic_var.get()
        solution = None
        directions = []
        path_cost = 0
        explored_count = 0
        time_taken = 0

        if search_method == "BFS":
            solution, directions, path_cost, explored_count, time_taken = self.bfs_search()
        elif search_method == "DFS":
            solution, directions, path_cost, explored_count, time_taken = self.dfs_search()
        elif search_method == "A*":
            solution, directions, path_cost, explored_count, time_taken = self.astar_search(heuristic)

        if solution:
            self.animate_solution(solution, directions)
            self.solution_label.config(text=f"Path Cost: {path_cost}   |   Explored States: {explored_count}")
            self.time_label.config(text=f"Time Taken: {time_taken:.4f} ns")

        else:
            messagebox.showinfo("No Solution", "No solution was found using the selected method.")
            self.solution_label.config(text=f"No solution")
            self.time_label.config( text="Time Taken: 0.0000 ns", font=('Helvetica', 14))  # Reset time taken if no solution found



    # -----------------------------------------------------------------------------------------
    # TODO: Function for importing puzzle.in file
    # >>> Insert the function you made in the pre-lab activity 1
    # -----------------------------------------------------------------------------------------
    def import_configuration(self):
        file_path = filedialog.askopenfilename(title="Select Puzzle File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not file_path:
            return  # If no file is selected, return without doing anything

        try:
            with open(file_path, 'r') as file:
                tiles = []
                for line in file:
                    tiles.append([int(num) for num in line.split()])

                if len(tiles) != 3 or any(len(row) != 3 for row in tiles):
                    raise ValueError("Invalid puzzle configuration: Must be a 3x3 grid")

                if not self.validate_tiles(tiles):
                    raise ValueError("Invalid puzzle configuration: Must contain numbers 0-8")

                # Update the initial and saved node with the imported configuration
                empty_tile = self.find_empty_spot(tiles)
                self.initial_node = Node(tiles, empty_tile)
                self.saved_node = Node([row[:] for row in tiles], empty_tile)
                self.load_tiles(self.initial_node.state)
                self.check_solvability(self.initial_node.state)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import configuration: {e}")

        

    # -----------------------------------------------------------------------------------------
    # TODO: Checks the number of inversion; whether the tile is solvable or not
    # @params:
    #	tiles - puzzle state
    # Notes:
    #   * Configure the self.solution_label if the puzzle can arrive to a winning state or not upon loading the input file
    # -----------------------------------------------------------------------------------------
    def check_solvability(self, tiles):

        flattened = [num for row in tiles for num in row if num != 0]
        inversions = 0

        for i in range(len(flattened)):
            for j in range(i + 1, len(flattened)):
                if flattened[i] > flattened[j]:
                    inversions += 1
        if inversions % 2 == 0:
            self.solution_label.config(text="Puzzle is Solvable", fg='green')
        else:
            self.solution_label.config(text="Puzzle is Not Solvable", fg='red')
    

    
    # -----------------------------------------------------------------------------------------
    # TODO: Applies all legal actions and gets the resulting states
    # @params
    #   node - data structure of a state
    # @return
    #   neighbors - a list of nodes (data structures) of resulting states given a legal action (move)
    # Note:
    #   To match the test cases, follow the U D R L sequence of action search
    # -----------------------------------------------------------------------------------------
    def get_neighbors(self, node):
        
        # intialize neighbors array -> will store the resulting neighbor nodes after applying all the legal moves
        neighbors = []

        # gets the position of the empty_tile -> represented by 0
        x,y = node.empty_tile

        # stores the current game state
        tiles = node.state

        # possible movements
        actions = [
            ('U', -1, 0),
            ('D', 1, 0),
            ('R', 0, 1),
            ('L', 0, -1),
        ]

        # iterates all the possible movement and updates the new position of the empty tile after the move
        for action, dx, dy in actions:
            new_x, new_y = x + dx, y + dy

            # checker to see if position is within bounds
            if 0 <= new_x < 3 and 0 <= new_y < 3:
                # creates a copy of the current game state 
                # ensures that the original state is not affected by the changes
                new_tiles = [row[:] for row in tiles]
                # swap elements 
                new_tiles[x][y], new_tiles[new_x][new_y] = new_tiles[new_x][new_y], new_tiles[x][y]
                # creates a new node object
                # new_tiles -> updated game state
                # (new_x, new_y) -> new position of the empty tile (0)
                # action -> action taken (U, D, L, or R)
                # node -> node before 
                # node.path_cost -> new path cost 
                new_node = Node(new_tiles, (new_x, new_y), action, node, node.path_cost + 1)
                # append the new_node to the neighbors list
                neighbors.append(new_node)

        return neighbors

    # -----------------------------------------------------------------------------------------
    # Returns the path (a list of states), directions (a list of actions), and path cost
    # @params:
    #	node - data structure representing a state
    # @return
    #   * path - an array of states from the given node up to its predecessors
    #   * directions - an array of actions taken from the current state up to its predecessors
    #   * path_cost - distance from the initial state to the current state
    # -----------------------------------------------------------------------------------------
    def get_path(self, node):

        # initialize list for storing the path it takes to get to initial to the goal
        path = []

        # initialize list for storing the actions done to get to the goal from initial
        directions = []

        # get the path cost
        path_cost = node.path_cost

        # get the goal node and set is as the current
        current_node = node

        # loop for backtracking the nodes
        while current_node:
            # adds the current node the the path array
            path.append(current_node.state)

            # checks the action of the node 
            if current_node.action:
                # appends the action of the node (U, D, L, or R) to the directions array 
                directions.append(current_node.action)
            
            # move to the parent node of the current node -> allows backtracking
            current_node = current_node.parent

        # reverses the path array to display the path from initial to goal
        # reverses the directions array to display the path from initial to goal
        # returns the path_cost
        return path[::-1], directions[::-1], path_cost


    # -----------------------------------------------------------------------------------------
    # TODO: Implements Breadth-First Search
    # @return
    #   * solution - an array of the states from initial to goal state
    #   * directions - array of actions taken from initial to goal state
    #   * path_cost - distance from initial to goal
    #   * explored_count - number of states put in explored (closed) list
    # -----------------------------------------------------------------------------------------
    @profile
    def bfs_search(self):

        start_time = time.time_ns()
        
        # double ended queue to perform BFS -> will hold the nodes to be explored
        frontier = deque([self.initial_node])

        # store explored state as tuples -> avoids duplicate and easier to compare since it is immutable
        explored = set()

        # counter for the explored nodes
        explored_count = 0

        # loop when there are nodes left in the frontier
        while frontier:

            # pop the leftmost node in the frontier
            node = frontier.popleft()
            # increment explored_count
            explored_count += 1

            # check if the current state is already the goal state
            if node.state == self.goal_tiles:
                # gets the value of the solution path, the direction used, and the path_cost
                solution, directions, path_cost = self.get_path(node)
                end_time = time.time_ns()
                time_taken = end_time - start_time
                return solution, directions, path_cost, explored_count, time_taken
            
            # add the current_state to the explored set
            # convert into a tuple of a tuple to make it easier 
            # IMMUTABLE -> state of the explored set won't change
            # HASHABLE -> consistent hash value making it easier to store and check the states
            explored.add(tuple(tuple(row) for row in node.state))

            # generate all possible valid states -> moves the empty tile in the current tile
            for neighbor in self.get_neighbors(node):
                # convert neighbor state as a tuple
                neighbor_state_tuple = tuple(tuple(row) for row in neighbor.state)
                # checks if the neighbor is not explored
                if neighbor_state_tuple not in explored:
                    frontier.append(neighbor)
                    # avoid duplicate
                    explored.add(neighbor_state_tuple) 
        # If no solition was found, return empty
        end_time = time.time_ns()
        time_taken = end_time - start_time
        return None, [], 0, explored_count, time_taken

    # -----------------------------------------------------------------------------------------
    # TODO: Implements Depth-First Search
    # @return
    #   * solution - an array of the states from initial to goal state
    #   * directions - array of actions taken from initial to goal state
    #   * path_cost - distance from initial to goal
    #   * explored_count - number of states put in explored (closed) list
    # -----------------------------------------------------------------------------------------
    @profile
    def dfs_search(self):
        
        start_time = time.time_ns()

        # stack for DFS
        frontier = [self.initial_node]

        # store explored state as tuples -> avoids duplicate and easier to compare since it is immutable
        explored = set()

        # counter for the explored nodes
        explored_count = 0

        # loop when there are still nodes in the frontier
        while frontier:
            
            # pop the rightmost node
            node = frontier.pop()
            
            # increment the explore_count
            explored_count += 1

            # check if the current state is already the goal state
            if node.state == self.goal_tiles:
                # gets the value of the solution path, the direction used, and the path_cost
                solution, directions, path_cost = self.get_path(node)
                end_time = time.time_ns()
                time_taken = end_time - start_time
                return solution, directions, path_cost, explored_count, time_taken
            
            # add the current_state to the explored set
            # convert into a tuple of a tuple to make it easier 
            # IMMUTABLE -> state of the explored set won't change
            # HASHABLE -> consistent hash value making it easier to store and check the states
            explored.add(tuple(tuple(row) for row in node.state))

            # generate all possible valid states -> moves the empty tile in the current tile
            for neighbor in self.get_neighbors(node):
                # convert neighbor state as a tuple
                neighbor_state_tuple = tuple(tuple(row) for row in neighbor.state)
                # checks if the neighbor is not explored and is not in the frontiee
                if neighbor_state_tuple not in explored:
                    frontier.append(neighbor)
        # If no solition was found, return empty
        end_time = time.time_ns()
        time_taken = end_time - start_time
        return None, [], 0, explored_count, time_taken
    
    # -----------------------------------------------------------------------------------------
    # TODO: Implements A* Search
    # @return
    #   * solution - an array of the states from initial to goal state
    #   * directions - array of actions taken from initial to goal state
    #   * path_cost - distance from initial to goal
    #   * explored_count - number of states put in explored (closed) list
    # Note:
    #   Write the values of fn, gn, and hn when searching for neighbors (successors) of the current state
    #   You may open the file in this function or create a helper function just for storing the values
    # -----------------------------------------------------------------------------------------
    def astar_search(self, heuristic):
        start_time = time.time_ns()
        
        # Initialize the frontier as a priority queue (min-heap)
        frontier = []
        # Dictionary to keep track of the lowest fn values for states in the frontier
        frontier_states = {}
        # Set to keep track of explored states
        explored = set()
        # Set to keep track of logged states for evaluation output
        logged_states = set()
        
        # Start node is the initial node
        start_node = self.initial_node
        start_node.gn = 0  # Cost from start
        start_node.hn = self.calculate_heuristic(start_node.state, heuristic)  # Heuristic cost
        start_node.fn = start_node.gn + start_node.hn  # Total cost
        
        # Push the start node into the frontier and track it in the dictionary
        heapq.heappush(frontier, (start_node.fn, start_node))
        frontier_states[tuple(map(tuple, start_node.state))] = start_node.fn
        
        # Explored count
        explored_count = 1

        # Open the evaluation output file
        with open("evaluation.out", "w") as f:
            # Main search loop
            while frontier:
                # Pop the node with the smallest fn value from the frontier
                _, current_node = heapq.heappop(frontier)
                current_state = tuple(map(tuple, current_node.state))
                
                if current_node != start_node:
                    # Log the current node's fn, gn, and hn values if not already logged
                    if current_state not in logged_states:
                        f.write(f"f(n)={current_node.fn}, g(n)={current_node.gn}, h(n)={current_node.hn}\n")
                        logged_states.add(current_state)

                # Check if the current node is the goal state
                if current_node.state == self.goal_tiles:
                    # Return the solution, directions, path cost, explored count, and time taken
                    solution, directions, path_cost = self.get_path(current_node)
                    end_time = time.time_ns()
                    time_taken = end_time - start_time
                    return solution, directions, path_cost, explored_count, time_taken
                
                # Add the current node to the explored set
                explored.add(current_state)
                explored_count += 1
                
                # Get the neighbors of the current node
                neighbors = self.get_neighbors(current_node)
                for neighbor in neighbors:
                    # Convert the neighbor's state to a tuple
                    neighbor_state = tuple(map(tuple, neighbor.state))
                
                    # Neighbor is already explored, skip
                    if neighbor_state in explored:
                        continue
                    
                    # Calculate gn, hn, and fn for the neighbor
                    neighbor.gn = current_node.gn + 1  # Increment cost from start
                    neighbor.hn = self.calculate_heuristic(neighbor.state, heuristic)  # Heuristic cost
                    neighbor.fn = neighbor.gn + neighbor.hn  # Total cost

                    # Log the neighbor's fn, gn, and hn values if not already logged
                    if neighbor_state not in logged_states:
                        f.write(f"f(n)={neighbor.fn}, g(n)={neighbor.gn}, h(n)={neighbor.hn}\n")
                        logged_states.add(neighbor_state)
                    
                    # If the neighbor is not in the frontier or has a lower fn value (better path)
                    if (neighbor_state not in frontier_states) or (neighbor.fn < frontier_states[neighbor_state]):
                        # Push the neighbor to the frontier
                        heapq.heappush(frontier, (neighbor.fn, neighbor))
                        # Update or add the neighbor's state and fn value in frontier_states
                        frontier_states[neighbor_state] = neighbor.fn
        
        # If no solution is found, return failure values
        end_time = time.time_ns()
        time_taken = end_time - start_time
        return None, [], 0, explored_count, time_taken

    # -----------------------------------------------------------------------------------------
    # Given a type of heuristic, get the hn
    # @params
    #   state - the configuration of the puzzle
    #   heuristic - string; got from the dropdown menu
    # -----------------------------------------------------------------------------------------
    def calculate_heuristic(self, state, heuristic):
        if heuristic == "Manhattan Distance":
            return self.manhattan_distance(state)
        elif heuristic == "Misplaced Tiles":
            return self.misplaced_tiles(state)
        elif heuristic == "Adjacent Tiles":
            return self.adjacent_tiles(state)
        return 0

    # -----------------------------------------------------------------------------------------
    # TODO: Calculates Manhattan Distance
    # @params
    #   state - the configuration of the puzzle
    # @return
    #   hn - heuristic; sum of manhattan distances
    # -----------------------------------------------------------------------------------------
    def manhattan_distance(self, state):
        goal_positions = {
            1: (0, 0), 2: (0, 1), 3: (0, 2),
            4: (1, 0), 5: (1, 1), 6: (1, 2),
            7: (2, 0), 8: (2, 1), 0: (2, 2) 
        }
        
        hn = 0
        for i in range(3):
            for j in range(3):
                tile = state[i][j]
                if tile != 0:  # We don't calculate the Manhattan distance for the empty tile
                    goal_x, goal_y = goal_positions[tile]
                    hn += abs(i - goal_x) + abs(j - goal_y)  # Manhattan distance formula

        return hn

    # -----------------------------------------------------------------------------------------
    # TODO: Calculates Misplaced Tiles
    # @params
    #   state - the configuration of the puzzle
    # @return
    #   hn - heuristic; count of misplaced tile (excluding the empty tile)
    # -----------------------------------------------------------------------------------------
    def misplaced_tiles(self, state):
        goal_tiles = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]  # The goal state for the puzzle
        ]
        
        hn = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != 0 and state[i][j] != goal_tiles[i][j]:  # Exclude empty tile
                    hn += 1  # Increment count if tile is misplaced

        return hn

    # -----------------------------------------------------------------------------------------
    # TODO: Calculates Non-Adjacent Tiles
    # @params
    #   state - the configuration of the puzzle
    # @return
    #   hn - heuristic; count of non-adjacent tiles (both horizontally and vertically)
    # -----------------------------------------------------------------------------------------
    def adjacent_tiles(self, state):
        goal = [
            (1, 2), (1, 4),
            (2, 3), (4, 7),
            (4, 5), (2, 5),
            (5, 6), (5, 8),
            (7, 8), (3, 6),
            (8, 0), (6, 0)
        ]

        adjacent = []
        for i in range(3):
            for j in range(2):
                adjacent.append((state[i][j], state[i][j + 1]))
                adjacent.append((state[j][i], state[j + 1][i]))

        non_adj = 0
        for adj in adjacent:
            if adj not in goal:
                non_adj += 1

        return non_adj
# Create and run the app
root = tk.Tk()
app = PuzzleApp(root)
root.mainloop()