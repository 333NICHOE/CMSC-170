import tkinter as tk
from tkinter import filedialog, messagebox

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
    
    # def __lt__(self, other):
    #     return self.path_cost < other.path_cost

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
        author_label = tk.Label(header_frame, text="Student Name", font=('Helvetica', 14))
        author_label.pack()
        
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

        if search_method == "BFS":
            solution, directions, path_cost, explored_count = self.bfs_search()
        elif search_method == "DFS":
            solution, directions, path_cost, explored_count = self.dfs_search()
        elif search_method == "A*":
            solution, directions, path_cost, explored_count = self.astar_search(heuristic)

        if solution:
            self.animate_solution(solution, directions)
            self.solution_label.config(text=f"Path Cost: {path_cost}   |   Explored States: {explored_count}")
        else:
            messagebox.showinfo("No Solution", "No solution was found using the selected method.")
            self.solution_label.config(text=f"No solution")
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
    # >>> Insert the function you made in the pre-lab activity 1
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
    # >>> Insert the function you made in exercise 1
    # -----------------------------------------------------------------------------------------
    def get_neighbors(self, node):
        neighbors = []
        x,y = node.empty_tile
        tiles = node.state
        actions = [
            ('U', -1, 0),
            ('D', 1, 0),
            ('R', 0, 1),
            ('L', 0, -1),
        ]
        for action, dx, dy in actions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 3 and 0 <= new_y < 3:
                new_tiles = [row[:] for row in tiles]
                new_tiles[x][y], new_tiles[new_x][new_y] = new_tiles[new_x][new_y], new_tiles[x][y]
                new_node = Node(new_tiles, (new_x, new_y), action, node, node.path_cost + 1)
                neighbors.append(new_node)
        return neighbors
    
    # -----------------------------------------------------------------------------------------
    # TODO: Returns the path (a list of states), directions (a list of actions), and path cost
    # @params:
    #	node - data structure representing a state
    # @return
    #   * solution - an array of the states from initial to goal state
    #   * directions - array of actions taken from initial to goal state
    #   * path_cost - distance from initial to goal
    # >>> Insert the function you made in exercise 1
    # -----------------------------------------------------------------------------------------
    def get_path(self, node):
        path = []
        directions = []
        path_cost = node.path_cost
        current_node = node
        # loop for backtracking the nodes
        while current_node:
            path.append(current_node.state)
            if current_node.action:
                directions.append(current_node.action)
            current_node = current_node.parent
        return path[::-1], directions[::-1], path_cost
    # -----------------------------------------------------------------------------------------
    # TODO: Implements A* Search
    # @return
    #   * solution - an array of the states from initial to goal state
    #   * directions - array of actions taken from initial to goal state
    #   * path_cost - distance from initial to goal
    #   * explored_count - number of states put in explored (closed) list
    # Note:
    #   Write the falues of fn, gn, and hn when searching for neighbors (successors) of the current state
    #   You may open the file in this function or create a helper function just for storing the values
    # -----------------------------------------------------------------------------------------
    def astar_search(self, heuristic):
        pass

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
        pass

    # -----------------------------------------------------------------------------------------
    # TODO: Calculates Misplaced Tiles
    # @params
    #   state - the configuration of the puzzle
    # @returns
    #   hn - heuristic; count of misplaced tile (excluding the empty tile)
    # -----------------------------------------------------------------------------------------
    def misplaced_tiles(self, state):
        pass

    # -----------------------------------------------------------------------------------------
    # TODO: Calculates Non-Adjacent Tiles
    # @params
    #   state - the configuration of the puzzle
    # @return
    #   hn - heuristic; count of non-adjacent tiles (both horizontally and vertically)
    # -----------------------------------------------------------------------------------------
    def adjacent_tiles(self, state):
        pass
# Create and run the app
root = tk.Tk()
app = PuzzleApp(root)
root.mainloop()