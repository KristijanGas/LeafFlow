

from linkedList import LinkedList


class visualPreparator:

    def __init__(self,tree_size,root,ConnectsToEdges,ConnectsTo):
        self.tree_size = tree_size
        self.root = root
        self.ConnectsToEdges = ConnectsToEdges
        self.ConnectsTo = ConnectsTo
        self.vertexPositioning = []
        for i in range(self.tree_size+1):
            self.vertexPositioning.append([0,0])
    

    def initPositions(self,spacingMultiplier,vertexRadius):
        self.radiusRestriction = []
        bfs = LinkedList()
        bfs.push_back(self.root)

        #while bfs.size != 0:
        #    curNode = bfs.pop_back(self.root)
        #    if curNode == self.root:


                
        #self.radiusRestriction.append([{"x" : 0, "y" : 0 ,"r" : 2*vertexRadius+spacingMultiplier*vertexRadius}])