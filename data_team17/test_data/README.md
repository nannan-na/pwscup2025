## 機械学習モデルDの有用性評価用データセット
- test_data1.csv：Ai.csv（仮）とB17_1.csvから作成したモデルDの有用性評価用データセット

    ※値域内かは不明
- （以下作成したテストデータを追加）

## データセットの作成手順
1. HI_100K.csv、MA_100K.csvそれぞれより5万レコードを抽出し、結合（=Ai.csv）
    - utilのrandom_sampling.py、concat_csv.pyを利用
2. Ai.csvのデータが予選データセットの値域内に収まるかを確認
    - utilのcheck_csv.pyを利用
    * dataのpre_columns_range.jsonの各特徴量のカテゴリがcheck_csv.pyのカテゴリに含まれていないため使えない？？
    - 値域外のデータが含まれる場合は、1.からやり直し
3. Ai.csvより5000レコード、B17_i.csvより5000レコード抽出、結合（= tmp.csv）
4. tmp.csv内に重複するレコードがないかチェック
    - utilのcheck_duplicates.pyを利用
    - 重複がある場合は、3.からやりなおし
5. tmp.csvのレコードをランダムに入れ替えて、test_datai.csvを作成
    - anonymazationのrandomshuffle_rows.pyを利用