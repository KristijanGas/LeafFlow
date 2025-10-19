

import math
from centroidfind import findCentroid
from linkedList import LinkedList
from tree_generator import TreeGeneratorBranching


class visualPreparator:

    def __init__(self,tree_size,root,ConnectsTo):
        self.tree_size = tree_size
        self.root = root
        self.ConnectsTo = ConnectsTo
        self.vertexPositioning = {}
        self.visited = []
        for i in range(self.tree_size+1):
            self.visited.append(0)
    

    def checkCollision(self, ignoreParent, originx, originy, directionAngle, radiusRestriction):
        closestHitDist = float('inf')
        closestHitIndex = -1

        dx = math.cos(directionAngle)
        dy = math.sin(directionAngle)

        for i, circle in enumerate(radiusRestriction):
            if circle["node"] == ignoreParent:
                continue

            cx = circle["x"]
            cy = circle["y"]
            r = circle["r"]
            # Vector from origin to circle center
            fx = cx - originx
            fy = cy - originy

            # projection length of center onto the ray direction (may be negative)
            t = fx * dx + fy * dy

            # closest point on infinite line (ray) to circle center
            closestX = originx + t * dx
            closestY = originy + t * dy

            # squared distance from circle center to that closest point
            distSq = (closestX - cx) ** 2 + (closestY - cy) ** 2

            # consider collision only if projection is in front of origin (t >= 0)
            # and the distance to the line is less than or equal to radius
            disToHit = self.pointsDistance(cx,cy,originx,originy)
            if t >= 0 and distSq <= (r * r)-0.1:
                if t < closestHitDist:
                    closestHitDist = t
                    closestHitIndex = i
        return closestHitIndex

    def pointsDistance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
    def angleFromOrigin(self,x1,y1):
        return math.atan2(y1,x1)

    def angleToVector(self, angle):
        x = math.cos(angle)
        y = math.sin(angle)
        return (x, y)
    def radiusRestriction(self,spacingMultiplier,vertexRadius):
        return vertexRadius+spacingMultiplier*vertexRadius/2.5
    
    def initPositionsPropagating(self,spacingMultiplier,vertexRadius):
        radiusRestriction = []

        bfs = LinkedList()
        bfs.push_back(self.root)

        while bfs.size != 0:
            curNode = bfs.pop_back()
            self.visited[curNode] = 1
            parent = -1
            for adjecent in self.ConnectsTo[curNode]:
                if self.visited[adjecent] == 0:
                    bfs.push_front(adjecent)
                else:
                    parent = adjecent
            childrenCount = len(self.ConnectsTo[curNode])
            if curNode == self.root:
                centerAngle = 0
                minAngle = centerAngle-math.pi
                maxAngle = centerAngle+math.pi
                self.vertexPositioning[curNode] = {"x" : 0, "y" : 0, "node" : curNode}
                radiusRestriction.append({"node": curNode,"x" : 0, "y" : 0 ,"r" : self.radiusRestriction(spacingMultiplier,vertexRadius)})
                #print("node:",curNode,"x:",0,"y:",0)
                totalRange = maxAngle-minAngle
                singleAngleAdd = totalRange/childrenCount

                for i in range(childrenCount):
                    adjecent = self.ConnectsTo[curNode][i]
                    newx, newy = self.angleToVector(singleAngleAdd/2 + singleAngleAdd*i+minAngle)
                    newx*=vertexRadius*spacingMultiplier
                    newy*=vertexRadius*spacingMultiplier
                    radiusRestriction.append({"node": adjecent,"x" : newx, "y" : newy ,"r" : self.radiusRestriction(spacingMultiplier,vertexRadius)})
                    self.vertexPositioning[adjecent] = {"x" : newx, "y" : newy, "node" : adjecent}
                    #print("node:",adjecent,"x:",newx,"y:",newy)
            else:
                
                if childrenCount == 0:
                    continue
                curx = self.vertexPositioning[curNode]["x"]
                cury = self.vertexPositioning[curNode]["y"]
                centerAngle = self.angleFromOrigin(curx,cury)
                minAngle = centerAngle-math.pi
                maxAngle = centerAngle+math.pi
                dAlpha = centerAngle
                while dAlpha <= maxAngle:
                    collided = self.checkCollision(curNode,curx,cury,dAlpha,radiusRestriction)
                    if collided != -1:
                        maxAngle = dAlpha
                        break
                    dAlpha += 0.01
                dAlpha = centerAngle
                while dAlpha >= minAngle:
                    collided = self.checkCollision(curNode,curx,cury,dAlpha,radiusRestriction)
                    if collided != -1:
                        minAngle = dAlpha
                        break
                    dAlpha -= 0.01
                totalRange = maxAngle-minAngle
                singleAngleAdd = totalRange/childrenCount
                i = 0
                nodesDrawn = 0
                while i < childrenCount:
                    adjecent = self.ConnectsTo[curNode][i]
                    if adjecent == parent:
                        i+=1
                    if i >= childrenCount:
                        break
                    adjecent = self.ConnectsTo[curNode][i]
                    newx, newy = self.angleToVector(singleAngleAdd*(nodesDrawn+1)+minAngle)
                    newx*=vertexRadius*spacingMultiplier
                    newy*=vertexRadius*spacingMultiplier
                    newx+=curx
                    newy+=cury
                    radiusRestriction.append({"node": adjecent,"x" : newx, "y" : newy ,"r" : self.radiusRestriction(spacingMultiplier,vertexRadius)})
                    self.vertexPositioning[adjecent] = {"x" : newx, "y" : newy, "node" : adjecent}
                    #print("node:",adjecent,"x:",newx,"y:",newy)
                    i+=1
                    nodesDrawn+=1
        return self.vertexPositioning

    def calculateSubTreeSizes(self):
        # Compute subtree sizes for every node and store in self.subTreeSizes
        # Uses DFS from self.root to populate a dict mapping node -> size (# nodes in its subtree)
        def __dfs(u, parent):
            size = 1
            for v in self.ConnectsTo[u]:
                if v == parent:
                    continue
                size += __dfs(v, u)
            self.subTreeSizes[u] = size
            return size

        # initialize dict if missing
        if not hasattr(self, 'subTreeSizes') or self.subTreeSizes is None:
            self.subTreeSizes = {}
        # run DFS from root
        __dfs(self.root, -1)

    def initPositionsCircling(self,spacingMultiplier,vertexRadius):
        bfs = LinkedList()
        bfs.push_back(self.root)
        circleIndices = LinkedList()
        circleIndices.push_back(0)
        indexSize = {}

        for i in range(self.tree_size+1):
            indexSize[i] = 0
        indexSize[self.root] = self.tree_size
        self.subTreeSizes = {}
        angleRestrictions = {}
        angleRestrictions[self.root] = {"min":0,"max":2*math.pi}
        self.subTreeSizes[self.root] = self.tree_size

        self.calculateSubTreeSizes()
        lastCircleIndex = -1
        curAngle = 0
        while bfs.size != 0:
            curNode = bfs.pop_back()
            circleIndex = circleIndices.pop_back()
            self.visited[curNode] = 1
            parent = -1
            for adjecent in self.ConnectsTo[curNode]:
                if self.visited[adjecent] == 0:
                    bfs.push_front(adjecent)
                    circleIndices.push_front(circleIndex+1)
                    indexSize[circleIndex+1] += self.subTreeSizes[adjecent]
                else:
                    parent = adjecent
            minAngle = angleRestrictions[curNode]["min"]
            maxAngle = angleRestrictions[curNode]["max"]
            centerAngle = (minAngle+maxAngle)/2
            newx, newy = self.angleToVector(centerAngle)
            newx*=vertexRadius*spacingMultiplier*circleIndex
            newy*=vertexRadius*spacingMultiplier*circleIndex
            self.vertexPositioning[curNode] = {"x" : newx, "y" : newy, "node" : curNode}
            totalSubTreeSize = self.subTreeSizes[curNode]-1
            alreadyAssigned = 0
            for adjecent in self.ConnectsTo[curNode]:
                if adjecent == parent:
                    continue
                subTreeSize = self.subTreeSizes[adjecent]
                dAlpha = (maxAngle-minAngle)/totalSubTreeSize
                angleRestrictions[adjecent] = {"min": minAngle+dAlpha*(alreadyAssigned),"max":minAngle+dAlpha*(alreadyAssigned+subTreeSize)}
                alreadyAssigned+=subTreeSize
        return self.vertexPositioning

#example usage:
#


"""
n = 7
tg = TreeGeneratorBranching(n)
edges = tg.generateTree(2,300)
edges = [((1, 2), '?'),((1, 3), '?'),((1, 4), '?'),((1, 5), '?'),((5, 6), '?'),((6, 7), '?')]
print(edges)
centrFinder = findCentroid()
ConnectsTo = []
for i in range(n+1):
    ConnectsTo.append([])
for i in range(n-1):
    u = edges[i][0][0]
    v = edges[i][0][1]
    ConnectsTo[u].append(v)
    ConnectsTo[v].append(u)
centroid = centrFinder.find(ConnectsTo)
vp = visualPreparator(n, centroid, ConnectsTo)
positions = vp.initPositions(spacingMultiplier=2, vertexRadius=20)
"""