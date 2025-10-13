import sys
sys.setrecursionlimit(10000)

MOD = int(1e9 + 7)
N = 5005
INF = int(9e18)

POVCon = [[] for _ in range(N)]
res = 0
dp = [[0] * (N) for _ in range(N)]
def dfs(start, prev, edge, n):
    global res
    global dp
    if prev != start:
        size = len(POVCon[start])
        for i in range(size):
            if POVCon[start][i][0] != prev:
                dfs(POVCon[start][i][0], start, POVCon[start][i][1], n)

        if prev != -1:
            if size != 1:
                for j in range(n + 1):
                    ans = 1
                    for i in range(size):
                        if POVCon[start][i][0] != prev:
                            ans *= dp[POVCon[start][i][0]][j] % MOD
                            ans %= MOD

                    if edge in (1, 0):
                        dp[start][j + 1] = (dp[start][j + 1] + ans) % MOD
                    if edge in (-1, 0) and j > 0:
                        dp[start][j - 1] = (dp[start][j - 1] + ans) % MOD
            else:
                if edge in (1, 0):
                    dp[start][1] = 1
        else:
            for j in range(n + 1):
                ans = 1
                for i in range(size):
                    ans *= dp[POVCon[start][i][0]][j] % MOD
                    ans %= MOD
                res = (res + ans) % MOD

def main():
    global POVCon, res, dp
    t = int(input())
    for _ in range(t):
        n = int(input())
        dp.clear()
        dp = [[0] * (n + 3) for _ in range(n + 3)]

        for i in range(n + 1):
            POVCon[i].clear()

        for _ in range(n - 1):
            parts = input().split()
            u = int(parts[0])
            v = int(parts[1])
            w = parts[2]

            if w == ')':
                POVCon[u].append((v, 1))
                POVCon[v].append((u, -1))
            elif w == '?':
                POVCon[u].append((v, 0))
                POVCon[v].append((u, 0))
            else:
                POVCon[u].append((v, -1))
                POVCon[v].append((u, 1))

        res = 0
        for i in range(1, n + 1):
            if len(POVCon[i]) != 1:
                dfs(i, -1, -2, n)
                break

        print(res)

if __name__ == "__main__":
    main()
