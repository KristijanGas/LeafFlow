

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
            fx = originx - cx
            fy = originy - cy

            # Quadratic formula coefficients (based on ray-circle intersection)
            a = dx*dx + dy*dy
            b = 2 * (fx*dx + fy*dy)
            c = fx*fx + fy*fy - r*r

            discriminant = b*b - 4*a*c

            if discriminant < 0.2:
                # No intersection
                continue

            sqrt_d = math.sqrt(discriminant)

            # Two possible intersection distances along ray
            t1 = (-b - sqrt_d) / (2*a)
            t2 = (-b + sqrt_d) / (2*a)

            # Only consider points in front of the origin (t >= 0)
            valid_t = []
            if t1 >= 0:
                valid_t.append(t1)
            if t2 >= 0:
                valid_t.append(t2)

            if not valid_t:
                continue

            t_hit = min(valid_t)
            if t_hit < closestHitDist:
                closestHitDist = t_hit
                closestHitIndex = i

        return closestHitIndex


    def gradientFromOrigin(self,x1,y1,x2,y2):
        dist1 = math.sqrt(x1**2+y1**2)
        dist2 = math.sqrt(x2**2+y2**2)
        return (dist2-dist1)/math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
    def angleFromOrigin(self,x1,y1):
        if y1 < 0:
            return 2*math.pi + math.atan2(y1,x1)
        return math.atan2(y1,x1)

    def angleToVector(self, angle):
        x = math.cos(angle)
        y = math.sin(angle)
        return (x, y)

    def initPositions(self,spacingMultiplier,vertexRadius):
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
                radiusRestriction.append({"node": curNode,"x" : 0, "y" : 0 ,"r" : vertexRadius+spacingMultiplier*vertexRadius/2})
                print("node:",curNode,"x:",0,"y:",0)
                totalRange = maxAngle-minAngle
                singleAngleAdd = totalRange/childrenCount

                for i in range(childrenCount):
                    adjecent = self.ConnectsTo[curNode][i]
                    newx, newy = self.angleToVector(singleAngleAdd/2 + singleAngleAdd*i+minAngle)
                    newx*=vertexRadius*spacingMultiplier
                    newy*=vertexRadius*spacingMultiplier
                    radiusRestriction.append({"node": adjecent,"x" : newx, "y" : newy ,"r" : vertexRadius+spacingMultiplier*vertexRadius/4})
                    self.vertexPositioning[adjecent] = {"x" : newx, "y" : newy, "node" : adjecent}
                    print("node:",adjecent,"x:",newx,"y:",newy)
            else:
                
                if childrenCount == 0:
                    continue
                curx = self.vertexPositioning[curNode]["x"]
                cury = self.vertexPositioning[curNode]["y"]
                centerAngle = self.angleFromOrigin(curx,cury)
                minAngle = centerAngle-math.pi/2
                maxAngle = centerAngle+math.pi/2
                noCollisionBefore = -1
                dAlpha = minAngle
                while dAlpha <= maxAngle:
                    collided = self.checkCollision(curNode,curx,cury,dAlpha,radiusRestriction)
                    if noCollisionBefore == 1 and collided != -1:
                        maxAngle = dAlpha
                        break
                    if collided == -1:
                        noCollisionBefore = 1
                    if collided != -1:
                        minAngle = dAlpha
                    dAlpha += 0.01
                totalRange = maxAngle-minAngle
                singleAngleAdd = totalRange/childrenCount
                for i in range(childrenCount):
                    adjecent = self.ConnectsTo[curNode][i]
                    if adjecent == parent:
                        continue
                    newx, newy = self.angleToVector(singleAngleAdd/2 + singleAngleAdd*i+minAngle)
                    newx*=vertexRadius*spacingMultiplier
                    newy*=vertexRadius*spacingMultiplier
                    newx+=curx
                    newy+=cury
                    radiusRestriction.append({"node": adjecent,"x" : newx, "y" : newy ,"r" : vertexRadius+spacingMultiplier*vertexRadius/2})
                    self.vertexPositioning[adjecent] = {"x" : newx, "y" : newy, "node" : adjecent}
                    print("node:",adjecent,"x:",newx,"y:",newy)
        return self.vertexPositioning

#example usage:
#
n = 5
tg = TreeGeneratorBranching(n)
edges = tg.generateTree(2,300)

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
