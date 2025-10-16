

class findCentroid:
    ConnectsTo = []
    n = 0
    centroid = -1
    def __init__(self):
        pass
    def dfs(self,start,prev):
        size = self.ConnectsTo[start]
        maxSubtree = 0
        cnt = 0
        for u in size:
            if u != prev:
                res = self.dfs(u,start)
                cnt += res
                maxSubtree = max(maxSubtree,res) 
        maxSubtree = max(maxSubtree,self.n - cnt - 1)
        if maxSubtree < self.n/2:
            self.centroid = start
            #print("Centroid is: ",start)
        return cnt+1

    def find(self,edges): # edge ((u,v),type)
        self.n = len(edges)+1
        for i in range(self.n+1):
            self.ConnectsTo.append([])
        for i in range(self.n-1):
            u = edges[i][0][0]
            v = edges[i][0][1]
            self.ConnectsTo[u].append(v)
            self.ConnectsTo[v].append(u)

        self.dfs(1,-1)
        if self.centroid == -1:
            print("Error, centroid not found")
        return self.centroid

