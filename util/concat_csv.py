#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import pandas as pd

def main():
    ap = argparse.ArgumentParser(description="2つのヘッダー付きCSVを結合して出力")
    ap.add_argument("input_csv1", help="入力CSV1（ヘッダー付き）")
    ap.add_argument("input_csv2", help="入力CSV2（ヘッダー付き）")
    ap.add_argument("output_csv", help="出力CSV（ヘッダー付き）")
    args = ap.parse_args()

    # ファイル存在チェック
    for path in [args.input_csv1, args.input_csv2]:
        if not os.path.isfile(path):
            print(f"ERROR: ファイルが見つかりません: {path}", file=sys.stderr)
            sys.exit(1)

    # 文字列として読み込み（空文字も保持）
    df1 = pd.read_csv(args.input_csv1, dtype=str, keep_default_na=False, low_memory=False)
    df2 = pd.read_csv(args.input_csv2, dtype=str, keep_default_na=False, low_memory=False)

    # 縦方向に結合（行を追加）
    merged = pd.concat([df1, df2], ignore_index=True)

    # 出力
    merged.to_csv(args.output_csv, index=False)
    print(f"完了: {args.output_csv} に {len(merged)} 行を書き出しました（ヘッダー付き）。")

if __name__ == "__main__":
    main()
