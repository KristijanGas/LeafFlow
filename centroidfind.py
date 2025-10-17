

class findCentroid:
    ConnectsTo = []
    n = 0
    centroid = -1
    def __init__(self):
        pass
    def __dfs(self,start,prev):
        size = self.ConnectsTo[start]
        maxSubtree = 0
        cnt = 1
        for u in size:
            if u != prev:
                res = self.__dfs(u,start)
                cnt += res
                maxSubtree = max(maxSubtree,res) 
        maxSubtree = max(maxSubtree,self.n - cnt - 1)
        if maxSubtree < self.n/2:
            self.centroid = start
            #print("Centroid is: ",start)
        return cnt

    def find(self,ConnectsTo): # edge ((u,v),type)
        self.n = len(ConnectsTo)
        self.ConnectsTo = ConnectsTo
        self.__dfs(1,-1)
        if self.centroid == -1:
            print("Error, centroid not found")
        return self.centroid

