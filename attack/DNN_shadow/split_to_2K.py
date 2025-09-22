# 10万行のファイルを5分割して20001行ずつのExcelファイルに保存
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="CSVファイルをヘッダー+20000行ごとに5つに分割して保存"
    )
    parser.add_argument("input_csv", help="入力CSVファイルのパス")
    parser.add_argument("--prefix", default="split_file_2K",
                        help="出力ファイル名のプレフィックス (default: split_file)")
    args = parser.parse_args()

    input_file = args.input_csv
    output_prefix = args.prefix
    chunk_size = 20000  # データ行数（ヘッダーは別）

    # CSV読み込み
    df = pd.read_csv(input_file)

    total_rows = len(df)
    if total_rows < chunk_size * 5:
        print(f"⚠ 入力データが {chunk_size*5} 行未満です。出力ファイルの後半は空になります。")

    # 5分割
    for i in range(5):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size
        chunk = df.iloc[start_idx:end_idx]

        output_file = f"{output_prefix}_{i+1}.csv"
        chunk.to_csv(output_file, index=False)  # ヘッダー込み
        print(f"Saved {output_file} ({len(chunk)} rows + header)")

if __name__ == "__main__":
    main()
