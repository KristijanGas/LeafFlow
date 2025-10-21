import random
from collections import defaultdict
from solutionChecker import solutionChecker

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

#generates edge list of a tree with n nodes
class TreeGeneratorBranching:
    def __init__(self, n):
        if n % 2 !=1:
            raise ValueError("n must be odd")
        self.n = n
        self.nodes = [TreeNode(i) for i in range(1, n + 1)]
        self.adj_list = defaultdict(list)
    def __randint(self, a, b):
        if(a==b):
            return a
        return random.randint(a, b)    
    def convertEdges(self,edges):
        self.ConnectsTo = [[] for _ in range(self.n + 1)]
        self.ConnectsToEdges = [[] for _ in range(self.n + 1)]
        for i in range(self.n-1):
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
    def generateTree(self,maxbranchlen,fillrate):
        n = self.n
        have = 1
        Out = []
        Coloring = {}
        Red = [1]
        Coloring[1] = 1
        Mentions = {}

        while have != n:
            remain = n - have
            len_branch = self.__randint(1, min(remain, maxbranchlen) // 2) * 2
            size = len(Red)
            u = Red[self.__randint(0, size - 1)]
            for i in range(len_branch):
                Out.append(((u, have + 1), '?'))
                Mentions[u] = Mentions.get(u, 0) + 1
                Mentions[have + 1] = Mentions.get(have + 1, 0) + 1
                u = have + 1

                if i % 2 == 1:
                    Coloring[have + 1] = 1
                    Red.append(have + 1)

                have += 1
        fillCount = int(self.n * (fillrate / 1000))
        while fillCount > 0:
            edgeIndex = self.__randint(0, len(Out) - 1)
            u = Out[edgeIndex][0][0]
            v = Out[edgeIndex][0][1]
            if Out[edgeIndex][1] == '?':
                attempt = Out.copy()
                if random.randint(0, 1) == 0:
                    attempt[edgeIndex] = ((u, v), ')')
                else:
                    attempt[edgeIndex] = ((u, v), '(')
                self.convertEdges(attempt)
                solutionCheck = solutionChecker(self.ConnectsToEdges, self.n)
                possible = solutionCheck.checksol()
                if possible:
                    Out = attempt
                    fillCount -= 1
        print(fillCount)

        #print(Out[0][0][0])
        return Out

#[
#tg = TreeGeneratorBranching(11)
#edges = tg.generateTree(4,300)
#centrFinder = findCentroid()
#centroid = centrFinder.find(edges)
#print(centroid)

#for edge in edges:
#    print(edge[0][0],edge[0][1])
