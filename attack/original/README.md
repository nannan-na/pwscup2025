# オリジナルのメンバーシップ推定攻撃
運営提供のattack_Ci.py、attack_Di.py、attack_example.pyを使った攻撃精度を調査。

## attack_Ci.py（距離ベース）の攻撃精度
- C17_1.csv（takimoto）への攻撃

    （正解数）<font color="red"> 5042 / 10000</font>

    （得点）<font color="red"> 50.42 / 100</font>

- C17.csv（hirayama）への攻撃

    （正解数）<font color="red"> 945 / 10000</font>

    （得点）<font color="red"> 9.45 / 100</font>

- C17_1.csv（ano0）への攻撃

    （正解数）<font color="red"> 2074 / 10000</font>

    （得点）<font color="red"> 20.74 / 100</font>


## attack_Di.py（予測ラベルベース）の攻撃精度
※出力される1の数を10000に制限していない。
- model.json（takimoto）への攻撃

    （正解数）<font color="red"> 60793 / 100000</font>

- D17_1.json（hirayama）への攻撃

    （正解数）<font color="red"> 86487 / 100000</font>

- model.json（ano0）への攻撃

    （正解数）<font color="red"> 87217 / 100000</font>


## attack_Di.py（予測誤差ベース）の攻撃精度
※出力されるTRUEの数を10000に制限していない。
- model.json（takimoto）への攻撃

    （正解数）<font color="red"> 6487 / 10000</font>

    （得点）<font color="red"> 64.87 / 100</font>

- D17_1.json（hirayama）への攻撃

    （正解数）<font color="red"> 5146 / 10000</font>

    （得点）<font color="red"> 51.46 / 100</font>

- model.json（ano0）への攻撃

    （正解数）<font color="red"> 6038 / 10000</font>

    （得点）<font color="red"> 60.38 / 100</font>
