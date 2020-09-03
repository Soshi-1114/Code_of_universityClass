## モジュール　インポート
import pulp
import pandas as pd
from itertools import product

# txtファイルの読み込み
## 空白を0に変更、整数値に変更
def Import_Data(data):
    df = pd.read_table(data,sep=",",header=None)
    df = df.fillna(0).astype(int)
    NP = df.values.tolist()
    return NP

# 2値(0,1)整数計画問題への定式化
## index：数独のマス番号、x：9*9*9の3次元2値変数配列
def Objective():
    problem = pulp.LpProblem()
    index = list(range(9))
    x = [[[pulp.LpVariable(f'x{i}{j}{k}', cat='Binary')
           for k in index] for j in index] for i in index]
    return problem,index,x

# 数独ルールによる制約条件の設定
def Constraints(index, problem, NP, x):
    ## 初期値を制約として設定：非零の要素をもつマスを総当たり法で判定
    for i, j in product(index, index):
        if NP[i][j] > 0:
            problem += x[i][j][NP[i][j]-1] == 1
            
    ## 制約１：各行iに1~9の各数値が入る
    for j, k in product(index, index):
        problem += pulp.lpSum(x[i][j][k] for i in index) == 1
        
    ## 制約２：各列jに1~9の各数値が入る
    for k, i in product(index, index):
        problem += pulp.lpSum(x[i][j][k] for j in index) == 1
        
    ## 制約３：3次元配列の各層kに1~9の各数値が入る
    for i, j in product(index, index):
        problem += pulp.lpSum(x[i][j][k] for k in index) == 1
        
    ## 制約４：3*3ブロック内に1~9の各数値が入る
    block_3 = [[l, l+1, l+2] for l in [0, 3, 6]]
    for m, n in product(block_3, block_3):
        for k in index:
            problem += pulp.lpSum(x[i][j][k] for i in m for j in n) == 1
    return problem

# 整数計画問題の実行可能解を求める
def Solver(problem, index, NP, x):
    ## 4並列処理、整数解を含む、Cutting Plane法(デフォルト)
    solver = pulp.PULP_CBC_CMD(threads=4,mip=True)
    problem.solve(solver)
    for i, j, k in product(index, index, index):
        if x[i][j][k].value() == 1:
            NP[i][j] = k + 1
    df = pd.DataFrame(NP)
    return df

def main():
    # データの読み込み
    data = 'sudoku.txt'
    NP = Import_Data(data)
    
    # 問題と変数の定義
    problem,index,x = Objective()
    
    # 数独ルールの制約の設定
    problem = Constraints(index, problem, NP, x)
    
    # Cutting Plane法で整数計画問題を解く
    df = Solver(problem, index, NP, x)
    return df

if __name__ == '__main__':
    df = main()
    print(df.values)