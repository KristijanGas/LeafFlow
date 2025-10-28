import random
from collections import defaultdict
from solutionChecker import solutionChecker

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

#generates edge list of a tree with n nodes
class TreeGeneratorBranching:
    def __init__(self, n,maxbranchlen,fillrate):
        if n % 2 !=1:
            raise ValueError("n must be odd")
        self.n = n
        self.maxbranchlen = maxbranchlen
        self.fillrate = fillrate
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
    def generateTree(self):
        n = self.n
        have = 1
        Out = []
        Coloring = {}
        Red = [1]
        Coloring[1] = 1
        Mentions = {}

        while have != n:
            remain = n - have
            len_branch = self.__randint(1, min(remain, self.maxbranchlen) // 2) * 2
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
        fillCount = int(self.n * (self.fillrate / 1000))
        fillCount = min(fillCount, len(Out))
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

        #print(Out[0][0][0])
        return Out


class TreeGeneratorExtending:
    def __init__(self, n,fillrate):
        if n < 3:
            raise ValueError("n should be bigger than 2")
        self.n = n
        self.fillrate = fillrate
        self.nodes = [TreeNode(i) for i in range(1, n + 1)]
        self.adj_list = defaultdict(list)
    def __randint(self, a, b):
        if(a==b):
            return a
        return random.randint(a, b)    
    def convertEdges(self,edges,treeSize):
        self.ConnectsTo = [[] for _ in range(treeSize + 1)]
        self.ConnectsToEdges = [[] for _ in range(treeSize + 1)]
        for i in range(treeSize-1):
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

    def findMinimalExtension(self,givenEdges):
        self.wrongParity = 0
        self.totalLeaves = 1
        self.unevenParity = []
        self.evenParity = []

        def __dfs(node,parent,parity):
            isLeaf = 1
            for neighbor in self.ConnectsTo[node]:
                if neighbor != parent:
                    isLeaf = 0
                    __dfs(neighbor,node,parity^1)

            if isLeaf:
                self.totalLeaves +=1
                if parity == 1:
                    self.wrongParity +=1
                    self.unevenParity.append(node)
                else:
                    self.evenParity.append(node)

        self.convertEdges(givenEdges,len(givenEdges)+1)

        for i in range(1,self.n+1):
            if len(self.ConnectsTo[i]) == 1:
                __dfs(i,-1,0)
                changeOdds = self.wrongParity
                changeEvens = self.totalLeaves - self.wrongParity
                self.evenParity.append(i)
                if changeOdds <= changeEvens:
                    return self.unevenParity
                else:
                    return self.evenParity

    def generateTree(self):
        curSize = 1
        actualSize = 1
        Out = []
        while actualSize < self.n:
            u = self.__randint(1, curSize)
            v = curSize + 1
            Out.append(((u, v), '?'))
            actualSize += 1
            toChange = self.findMinimalExtension(Out)
            if len(toChange) + actualSize <= self.n:
                curSize += 1
                if len(toChange) + actualSize == self.n:
                    toChange = self.findMinimalExtension(Out)
                    break
                continue
            else:
                Out.pop()
                actualSize -= 1

        toChange = self.findMinimalExtension(Out)

        for node in toChange:
            Out.append(((node, len(Out) + 2), '?'))
        self.convertEdges(Out,len(Out)+1)
        solutionCheck = solutionChecker(self.ConnectsToEdges, self.n)
        possible = solutionCheck.checksol()
        if not possible:
            print("Generated tree has no solution:")
            for edge in Out:
                print(edge[0][0],edge[0][1],edge[1])
            raise Exception("Generated tree has no solution")
        fillCount = int(self.n * (self.fillrate / 1000))
        fillCount = min(fillCount, len(Out))
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
                self.convertEdges(attempt, len(Out)+1)
                solutionCheck = solutionChecker(self.ConnectsToEdges, self.n)
                possible = solutionCheck.checksol()
                if possible:
                    Out = attempt
                    fillCount -= 1

        #print(Out[0][0][0])
        return Out

#[

'''
tg = TreeGeneratorExtending(330,300)
edges = tg.generateTree()
Edges = []


for edge in edges:
    print(edge[0][0],edge[0][1],edge[1])
'''