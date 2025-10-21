import json
import tkinter as tk
from gameCanvas import gameCanvas
from menuCanvas import menuCanvas
from gameDirector import gameDirector
from solutionChecker import solutionChecker
from tree_generator import TreeGeneratorBranching, TreeNode
WIDTH, HEIGHT = 1280, 720
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

class TreeVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeafFlow")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.ConnectsTo = []
        self.ConnectsToEdges = []
        self.current_level = 1
        self.menu = menuCanvas(self.root, self.load_level, self.free_play_game)
        self.menu.main_menu()
        


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

    def load_level(self, level_number):
        path = f"levels/main_levels/{level_number}.json"
        try:
            with open(path, 'r') as f:
                edges = json.load(f)
            self.tree_size = max(max(u, v) for (u, v), _ in edges)
            #print(edges)
            self.convertEdges(edges)
            self.start_tree_visualization()
        except FileNotFoundError:
            tk.messagebox.showinfo("Info", "No more levels available.")

    def free_play_game(self, tree_size):
        self.tree_size = tree_size
        self.ConnectsTo = []
        self.ConnectsToEdges = []
        while 1:
            tg = TreeGeneratorBranching(self.tree_size)
            edges = tg.generateTree(2,500)
            #edges = [((1, 2), '?'), ((2, 3), ')')]
            #print(self.tree_size)
            #for edge in edges:
                #print(edge[0][0],edge[0][1],edge[1])
            #print(edges)
            print(json.dumps(edges))
            self.convertEdges(edges)

            solutionCheck = solutionChecker(self.ConnectsToEdges,self.tree_size)
            possible = solutionCheck.checksol()
            if possible:
                break
        self.start_tree_visualization()

    def start_tree_visualization(self):
        

        self.gameDirector = gameDirector(self.tree_size,self.ConnectsToEdges,self.ConnectsTo,self.root,
                                         main_menu = self.menu.main_menu,
                                         next_level = self.next_level
                                         )
        self.gameDirector.prepareGame()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def next_level(self):
        self.tree_size+=2
        self.free_play_game(self.tree_size)

if __name__ == "__main__":
    root = tk.Tk()
    app = TreeVisualizerApp(root)
    root.mainloop()
