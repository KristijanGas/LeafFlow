



from centroidfind import findCentroid
from gameCanvas import gameCanvas
from visualPreparator import visualPreparator
import tkinter as tk

class gameDirector:

    def __init__(self,tree_size,ConnectsToEdges,ConnectsTo,root,main_menu):
        self.tree_size = tree_size
        self.ConnectsToEdges = ConnectsToEdges
        self.ConnectsTo = ConnectsTo
        self.vertexPositioning = {}
        self.root = root
        self.main_menu = main_menu
        self.node_radius = 8

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def prepareGame(self):
        centrFinder = findCentroid()
        self.tree_root = centrFinder.find(self.ConnectsTo)
    

        vp = visualPreparator(self.tree_size, self.tree_root, self.ConnectsTo)
        positions = vp.initPositionsPropagating(spacingMultiplier=2, vertexRadius=self.node_radius)
        self.positions = positions
        self.restartGame()

    def restartGame(self):
        self.definedEdges = {}
        self.playerSetEdges = {}
        self.clear_window()
        min_x = 1e9
        min_y = 1e9
        max_x = -1e9
        max_y = -1e9
        # positions is expected to be a dict mapping node -> { 'x':..., 'y':..., ... }
        for key, entry in self.positions.items():
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
        self.square_canvas = gameCanvas(self.root,main_menu_callback=self.main_menu,
                                   reset_edges_callback=self.restartGame,
                                   player_edge_assign=self.player_edge_assign
                                   )
        self.square_canvas.pack(fill=tk.BOTH, expand=True)
        

        # add nodes to canvas using normalized coordinates (0..1)
        for key, entry in self.positions.items():
            x = float(entry.get('x', entry.get('X')))
            y = float(entry.get('y', entry.get('Y')))

            nx = (x - min_x) / range_x
            ny = (y - min_y) / range_y
            # gameCanvas expects coordinates between 0 and 1
            node_id = key
            self.square_canvas.add_node(node_id, nx, ny,10*self.node_radius/maxRange)
        
        for u, nbrs in enumerate(self.ConnectsToEdges):
            for pair in nbrs:
                v = pair[0]
                direction = pair[1]
                if u == 0 or v == 0:
                    continue
                if u > v:
                    continue
                self.definedEdges[(u,v)] = direction
                self.square_canvas.add_edge(u, v,direction,color="grey")

    def player_edge_assign(self,u,v):
        dirChange = 1
        if u > v:
            u,v = v,u
            dirChange*=-1
        if (u,v) not in self.definedEdges:
            return
        if self.definedEdges[(u,v)] == 0:
            self.playerSetEdges[(u,v)] = dirChange
            self.square_canvas.add_edge(u,v,dirChange,color="royalblue")