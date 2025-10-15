import random
from collections import defaultdict
from centroidfind import findCentroid
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
    def randint(self, a, b):
        if(a==b):
            return a
        return random.randint(a, b)
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
            len_branch = self.randint(1, min(remain, maxbranchlen) // 2) * 2
            size = len(Red)
            u = Red[self.randint(0, size - 1)]
            for i in range(len_branch):
                Out.append(((u, have + 1), '?'))
                Mentions[u] = Mentions.get(u, 0) + 1
                Mentions[have + 1] = Mentions.get(have + 1, 0) + 1
                u = have + 1

                if i % 2 == 1:
                    Coloring[have + 1] = 1
                    Red.append(have + 1)

                have += 1

        for i in range(n - 1):
            u, v = Out[i][0]
            if Mentions.get(u, 0) > 1 and Mentions.get(v, 0) > 1:
                dothe = self.randint(1, 1000)
                if dothe < fillrate:
                    Out[i] = (Out[i][0], '(' if dothe % 2 == 0 else ')')
        print(Out[0][0][0])
        return Out


tg = TreeGeneratorBranching(11)
edges = tg.generateTree(4,300)
centrFinder = findCentroid()
centrFinder.find(edges)
#for edge in edges:
#    print(edge[0][0],edge[0][1])