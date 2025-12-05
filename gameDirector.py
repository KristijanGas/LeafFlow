import json
import copy
from centroidfind import findCentroid
from gameCanvas import gameCanvas
import solutionChecker
from visualPreparator import visualPreparator
import tkinter as tk

class gameDirector:

    def __init__(self,tree_size,ConnectsToEdges,ConnectsTo,root,main_menu,next_level,current_level,isFreeplay=False):
        self.tree_size = tree_size
        self.ConnectsToEdges = ConnectsToEdges
        self.ConnectsTo = ConnectsTo
        self.vertexPositioning = {}
        self.root = root
        self.main_menu = main_menu
        self.next_level_callback = next_level
        self.node_radius = 8
        self.current_level = current_level
        self.isFreeplay = isFreeplay
        self.doneLegit = True

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def prepareGame(self):
        centrFinder = findCentroid()
        self.tree_root = centrFinder.find(self.ConnectsTo)
        vp = visualPreparator(self.tree_size, self.tree_root, self.ConnectsTo)
        positions = vp.initPositionsCircling(spacingMultiplier=2, vertexRadius=self.node_radius)
        self.positions = positions
        self.restartGame()

    def restartGame(self):
        self.doneLegit = True
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
                                   reset_edges_callback=self.prepareGame,
                                   player_edge_assign=self.player_edge_assign,
                                   submit_result=self.submit_result,
                                   next_level=self.next_level,
                                   current_level=self.current_level,
                                   player_edge_remove=self.player_edge_remove,
                                   autocomplete_edge=self.auto_complete_next_step
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
                self.playerSetEdges[(u,v)] = direction
                self.square_canvas.add_edge(u, v,direction,color="grey")
        #for i in range(1,self.tree_size+1):
        #    self.square_canvas._add_number_to_node(i,i)
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
    
    def convertPlayerEdges(self):
        convertedEdges = copy.deepcopy(self.ConnectsToEdges)
        for j in range(self.tree_size+1):
            for i in range(len(convertedEdges[j])):
                v = convertedEdges[j][i][0]
                u = j
                dirChange = 1
                
                if u > v:
                    u,v = v,u
                    dirChange*=-1
                if self.ConnectsToEdges[j][i][1] == 0 and self.playerSetEdges[(u,v)] != 0:
                    convertedEdges[j][i][1] = dirChange * self.playerSetEdges[(u,v)]

        return convertedEdges

    def auto_complete_next_step(self):
        currentConnectsToEdges = self.convertPlayerEdges()
        solutionCheckerInstance = solutionChecker.solutionChecker(currentConnectsToEdges,self.tree_size)
        #print(currentConnectsToEdges)
        checkPossibility = solutionCheckerInstance.checksol()
        if self.check_result(): #already good
            self.square_canvas.canvas.create_text(
                self.square_canvas.canvas.winfo_width() // 2, 20,
                text="Already Good", fill="green",
                font=("Arial", 16, "bold")
            )
        self.doneLegit = False
        if checkPossibility == 0:
            self.square_canvas.canvas.create_text(
                self.square_canvas.canvas.winfo_width() // 2, 20,
                text="There is no solution from this position", fill="orange",
                font=("Arial", 16, "bold")
            )
        else:
            for u in range(1,self.tree_size+1):
                for pair in currentConnectsToEdges[u]:
                    v = pair[0]
                    direction = pair[1]
                    if direction == 0:
                        currentConnectsToEdges[u][currentConnectsToEdges[u].index(pair)][1] = 1
                        currentConnectsToEdges[v][currentConnectsToEdges[v].index([u,0])][1] = -1
                        solutionCheckerInstance = solutionChecker.solutionChecker(currentConnectsToEdges,self.tree_size)
                        if solutionCheckerInstance.checksol():
                            self.auto_complete_edge(u,v,1)
                            return
                        else:
                            currentConnectsToEdges[u][currentConnectsToEdges[u].index([v,1])][1] = -1
                            currentConnectsToEdges[v][currentConnectsToEdges[v].index([u,-1])][1] = 1
                            self.auto_complete_edge(u,v,-1)
                            return
            
        

    def auto_complete_edge(self,u,v,dir):
        dirChange = 1
        
        if u > v:
            u,v = v,u
            dirChange*=-1
        if (u,v) not in self.definedEdges:
            raise ValueError("Edge not defined")

        if self.definedEdges[(u,v)] == 0:
            self.playerSetEdges[(u,v)] = dir
            self.square_canvas.add_edge(u,v,dir,color="green")

    def submit_result(self):
        for entry in self.playerSetEdges:
            if self.playerSetEdges[entry] == 0:
                self.square_canvas._show_incompleteness(entry[0],entry[1])
                return
        correct = self.check_result()
        if correct:
            self.square_canvas.solved_correctly()
            if self.isFreeplay==False:
                self.updateProgress(self.current_level)
        else:
            self.square_canvas.solved_incorrectly(self.incorrect_sequence)


    def check_result(self):
        self.correct = 1
        self.incorrect_sequence = []
        for u, nbrs in enumerate(self.ConnectsToEdges):
            if len(nbrs) ==1:
                self.__dfs(u,-1,0)

        return self.correct
    
    def updateProgress(self, level):
        
        path = "levels/main_levels/progress_track.json"
        try:
            with open(path, 'r') as f:
                progress = json.load(f)
        except FileNotFoundError:
            progress = [0]*40
        if self.correct:
            try:
                if self.doneLegit:
                    progress[level-1] = 1
                    
                with open(path, 'w') as f:
                    json.dump(progress, f)
            except FileNotFoundError:
                pass

    def __dfs(self,start,parent,curvalue):
        entered = 0
        isInCorrect = 0
        if curvalue < 0:
            if self.correct == 1:
                self.correct = 0
                isInCorrect = 1
                self.incorrect_sequence.append(start)
                return isInCorrect
        for adjecent in self.ConnectsTo[start]:
            if adjecent != parent:
                entered+=1
                u = start
                v = adjecent
                direction = 1
                if u > v:
                    u,v = v,u
                    direction = -1
                value = self.playerSetEdges[(u,v)]
                ret = self.__dfs(adjecent,start,curvalue+value*direction)
                isInCorrect = max(ret,isInCorrect)
        if entered == 0 and curvalue !=0 and self.correct == 1:
            self.correct = 0
            isInCorrect = 1
        if isInCorrect:
            self.incorrect_sequence.append(start)
        return isInCorrect
    def next_level(self):
        self.next_level_callback()
        self.doneLegit = True
        
    def player_edge_remove(self,u,v):
        if u > v:
            u,v = v,u
        if (u,v) not in self.definedEdges:
            return
        if self.definedEdges[(u,v)] == 0:
            self.playerSetEdges[(u,v)] = 0
            self.square_canvas.add_edge(u,v,0,color="grey")