import tkinter as tk
import math
from gameCanvas import gameCanvas
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
        self.node_radius = 8

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

    def convertEdges(self,edges):
        self.ConnectsTo.clear()
        self.ConnectsToEdges.clear()
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
                self.ConnectsToEdges[u].append([v,-1])
                self.ConnectsToEdges[v].append([u,1])
            else:
                self.ConnectsToEdges[u].append([v,1])
                self.ConnectsToEdges[v].append([u,-1])

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
        #edges = [((1, 2), '?'), ((2, 3), ')')]

        print(edges)
        self.convertEdges(edges)
            
        centrFinder = findCentroid()
        self.tree_root = centrFinder.find(self.ConnectsTo)
    

        vp = visualPreparator(self.tree_size, self.tree_root, self.ConnectsTo)
        positions = vp.initPositionsPropagating(spacingMultiplier=2, vertexRadius=self.node_radius)

        self.clear_window()

        square_canvas = gameCanvas(self.root,main_menu_callback=self.main_menu)
        square_canvas.pack(fill=tk.BOTH, expand=True)

        min_x = 1e9
        min_y = 1e9
        max_x = -1e9
        max_y = -1e9
        # positions is expected to be a dict mapping node -> { 'x':..., 'y':..., ... }
        for key, entry in positions.items():
            x = float(entry.get('x', entry.get('X')))
            y = float(entry.get('y', entry.get('Y')))
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
        boundMultiplier = 1.2
        max_x*=boundMultiplier
        min_x*=boundMultiplier
        max_y*=boundMultiplier
        min_y*=boundMultiplier

        # guard against degenerate bounds
        range_x = max_x - min_x
        range_y = max_y - min_y
        
        if range_x == 0:
            range_x = 1.0
        if range_y == 0:
            range_y = 1.0
        maxRange = max(range_x,range_y)
        # add nodes to canvas using normalized coordinates (0..1)
        for key, entry in positions.items():
            x = float(entry.get('x', entry.get('X')))
            y = float(entry.get('y', entry.get('Y')))

            nx = (x - min_x) / range_x
            ny = (y - min_y) / range_y
            # gameCanvas expects coordinates between 0 and 1
            node_id = str(key)
            square_canvas.add_node(node_id, nx, ny,10*self.node_radius/maxRange)
        
        for u, nbrs in enumerate(self.ConnectsToEdges):
            for pair in nbrs:
                v = pair[0]
                direction = pair[1]
                if u == 0 or v == 0:
                    continue
                if u > v:
                    continue
                square_canvas.add_edge(str(u), str(v),direction,color="grey")


    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TreeVisualizerApp(root)
    root.mainloop()
