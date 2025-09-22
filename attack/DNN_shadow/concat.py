#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pandas as pd

def main():
    ap = argparse.ArgumentParser(description="Concatenate multiple CSV files into one (force comma-separated output, no header).")
    ap.add_argument("output_csv", help="出力先CSVファイル")
    ap.add_argument("input_csvs", nargs="+", help="結合する入力CSVファイル（5つ想定）")
    args = ap.parse_args()

    dfs = []
    for f in args.input_csvs:
        # 区切り文字を自動検出（タブかカンマかなど）
        try:
            df = pd.read_csv(f, sep=None, engine="python", header=None)
        except Exception as e:
            print(f"読み込みエラー: {f} ({e})")
            raise
        dfs.append(df)

    merged = pd.concat(dfs, axis=0, ignore_index=True)

    # 出力は必ずカンマ区切り
    merged.to_csv(args.output_csv, index=False, header=False)
    print(f"Saved merged CSV to {args.output_csv} ({merged.shape[0]} rows)")

if __name__ == "__main__":
    main()
