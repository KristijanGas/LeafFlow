import tkinter as tk
import math
from tree_generator import TreeGeneratorBranching, TreeNode
from centroidfind import findCentroid
from visualPreparator import visualPreparator

WIDTH, HEIGHT = 1280, 720
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

class TreeVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeafFlow")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.main_menu()
        self.ConnectsTo = []
        self.ConnectsToEdges = []

    def main_menu(self):
        self.clear_window()
        label = tk.Label(self.root, text="Enter a number (2-100):", font=("Arial", 14))
        label.pack(pady=10)

        self.number_entry = tk.Entry(self.root, font=("Arial", 14))
        self.number_entry.pack(pady=10)

        play_btn = tk.Button(self.root, text="Play", font=("Arial", 14), command=self.start_tree_visualization)
        play_btn.pack(pady=20)
    def add_main_menu_button(self):
        """
        Adds a 'Main Menu' button to the top-right corner of the window
        that calls self.mainmenu() when clicked.
        """
        # Create the button
        button = tk.Button(self.root, text="Main Menu", command=self.main_menu)

        # Use place() to position it in the top-right corner
        # with some padding from the top and right edges
        button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)  # 10px from right and top
    def start_tree_visualization(self):
        self.ConnectsTo = []
        self.ConnectsToEdges = []

        try:
            num = int(self.number_entry.get())
            if not 2 <= num <= 100:
                raise ValueError
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter a number between 2 and 100.")
            return
        self.tree_size = num
        tg = TreeGeneratorBranching(self.tree_size)
        edges = tg.generateTree(2,300)

        for i in range(self.tree_size+1):
            self.ConnectsTo.append([])
            self.ConnectsToEdges.append([])
        for i in range(self.tree_size-1):
            u = edges[i][0][0]
            v = edges[i][0][1]
            self.ConnectsTo[u].append(v)
            self.ConnectsTo[v].append(u)
            type = edges[i][1]
            
            if type == "?":
                self.ConnectsToEdges[u].append([v,0])
                self.ConnectsToEdges[v].append([u,0])
            elif type == ")":
                self.ConnectsToEdges[u].append([v,1])
                self.ConnectsToEdges[v].append([u,-1])
            else:
                self.ConnectsToEdges[u].append([v,-1])
                self.ConnectsToEdges[v].append([u,1])
            
        centrFinder = findCentroid()
        centroid = centrFinder.find(self.ConnectsTo)
        print("centroid: ",centroid)
        self.tree_root = centroid
        vp = visualPreparator(self.tree_size, centroid, self.ConnectsTo)
        positions = vp.initPositions(spacingMultiplier=3, vertexRadius=20)
        self.clear_window()
        self.show_tree(positions,10)
        self.add_main_menu_button()

    def show_tree(self, positions, nodeRadius):
        """
        Visualizes the tree nodes and edges on a resizable tkinter canvas.
        
        - positions: dict { node_id: {"x": float, "y": float, "node": node_id} }
        - nodeRadius: radius of the node circles
        - self.ConnectsToEdges: dict[node_id] = list of [connected_node, edge_type]
            where edge_type = 0 (undirected), 1/-1 (directed left/right)
        """

        self.positions = positions
        self.nodeRadius = nodeRadius

        window = self.root
        window.title("Tree Visualization")

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        target_width = screen_width
        target_height = int(screen_width * 9 / 16)

        if target_height > screen_height:
            target_height = screen_height
            target_width = int(screen_height * 16 / 9)

        # Create resizable canvas
        self.canvas = tk.Canvas(window, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Track bounds of logical coordinate system
        xs = [pos["x"] for pos in positions.values()]
        ys = [pos["y"] for pos in positions.values()]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)

        # Bind redraw on resize
        def on_resize(event):
            self.canvas.delete("all")
            self._draw_tree(event.width, event.height)

        self.root.bind("<Configure>", on_resize)

        # Initial draw
        self._draw_tree(target_width, target_height)

    def _draw_tree(self, canvas_width, canvas_height):
        
        padding = self.nodeRadius * 2

        span_x = max(self.max_x - self.min_x, 1)
        span_y = max(self.max_y - self.min_y, 1)

        def scale_x(x):
            return padding + (x - self.min_x) / span_x * (canvas_width - 2 * padding)

        def scale_y(y):
            return padding + (y - self.min_y) / span_y * (canvas_height - 2 * padding)

        screen_positions = {}

        # First scale and cache screen positions
        for entry in self.positions.values():
            sx = scale_x(entry["x"])
            sy = scale_y(entry["y"])
            screen_positions[entry["node"]] = (sx, sy)

        # Draw edges
        for u in range(1,len(self.ConnectsToEdges)):
            edges = self.ConnectsToEdges[u]
            for v, edge_type in edges:
                if u > v:
                    continue  # avoid drawing edges twice

                x1, y1 = screen_positions[u]
                x2, y2 = screen_positions[v]

                color = "black"
                arrow = None

                if edge_type == 0:
                    color = "gray"
                elif edge_type == 1:
                    color = "green"
                    arrow = "last"
                elif edge_type == -1:
                    color = "red"
                    arrow = "first"

                self.canvas.create_line(x1, y1, x2, y2, fill=color, arrow=arrow, width=2)

        # Draw nodes
        for node_id, (sx, sy) in screen_positions.items():
            x0 = sx - self.nodeRadius
            y0 = sy - self.nodeRadius
            x1 = sx + self.nodeRadius
            y1 = sy + self.nodeRadius

            self.canvas.create_oval(x0, y0, x1, y1, fill="skyblue", outline="black")
            self.canvas.create_text(sx, sy, text=str(node_id), font=("Arial", 10))





    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TreeVisualizerApp(root)
    root.mainloop()
