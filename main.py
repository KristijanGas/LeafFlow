import tkinter as tk
import math
from gameCanvas import gameCanvas
from gameDirector import gameDirector
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
        self.gameDirector = gameDirector(self.tree_size,self.ConnectsToEdges,self.ConnectsTo,self.root,main_menu = self.main_menu)
        self.gameDirector.prepareGame()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TreeVisualizerApp(root)
    root.mainloop()
