import tkinter as tk
import math
from tree_generator import TreeGeneratorBranching, TreeNode
from centroidfind import findCentroid

WIDTH, HEIGHT = 1280, 720
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

class TreeVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeafFlow")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.main_menu()

    def main_menu(self):
        self.clear_window()
        label = tk.Label(self.root, text="Enter a number (2-100):", font=("Arial", 14))
        label.pack(pady=10)

        self.number_entry = tk.Entry(self.root, font=("Arial", 14))
        self.number_entry.pack(pady=10)

        play_btn = tk.Button(self.root, text="Play", font=("Arial", 14), command=self.start_tree_visualization)
        play_btn.pack(pady=20)

    def start_tree_visualization(self):
        try:
            num = int(self.number_entry.get())
            if not 2 <= num <= 100:
                raise ValueError
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter a number between 2 and 100.")
            return
        self.tree_size = num
        tg = TreeGeneratorBranching(self.tree_size)
        edges = tg.generateTree(4,300)
        print(edges)
        centrFinder = findCentroid()
        centroid = centrFinder.find(edges)
        print("centroid: ",centroid)
        self.tree_root = centroid
        self.show_tree()

    def show_tree(self):
        self.clear_window()


    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TreeVisualizerApp(root)
    root.mainloop()
