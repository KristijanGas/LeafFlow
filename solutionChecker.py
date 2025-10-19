import sys
sys.setrecursionlimit(10000)

class solutionChecker:
    def __init__(self,ConnectsToEdge,tree_size):
        
        self.MOD = int(1e9 + 7)
        self.N = 5005
        self.INF = int(9e18)
        self.POVCon = ConnectsToEdge
        self.res = 0
        self.n = tree_size
        self.dp = [[0] * (self.N) for _ in range(self.N)]
        
    def dfs(self,start, prev, edge, n):
        if prev != start:
            size = len(self.POVCon[start])
            for i in range(size):
                if self.POVCon[start][i][0] != prev:
                    self.dfs(self.POVCon[start][i][0], start, self.POVCon[start][i][1], n)

            if prev != -1:
                if size != 1:
                    for j in range(n + 1):
                        ans = 1
                        for i in range(size):
                            if self.POVCon[start][i][0] != prev:
                                ans *= self.dp[self.POVCon[start][i][0]][j] % self.MOD
                                ans %= self.MOD

                        if edge in (1, 0):
                            self.dp[start][j + 1] = (self.dp[start][j + 1] + ans) % self.MOD
                        if edge in (-1, 0) and j > 0:
                            self.dp[start][j - 1] = (self.dp[start][j - 1] + ans) % self.MOD
                else:
                    if edge in (1, 0):
                        self.dp[start][1] = 1
            else:
                for j in range(n + 1):
                    ans = 1
                    for i in range(size):
                        ans *= self.dp[self.POVCon[start][i][0]][j] % self.MOD
                        ans %= self.MOD
                    self.res = (self.res + ans) % self.MOD

    def checksol(self):
        for i in range(1, self.n + 1):
            if len(self.POVCon[i]) != 1:
                self.dfs(i, -1, -2, self.n)
                break

        return self.res

