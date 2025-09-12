import sys
import pandas as pd
import numpy as np

# スワップ対象カラムをグループ分け
GROUPED_COLS = ["num_procedures", "num_medications", "encounter_count"]
INDEPENDENT_COLS = ["num_immunizations", "num_devices"]

# 年齢グループ定義
BINS = [0, 17, 44, 64, 74, np.inf]
LABELS = ["0-17", "18-44", "45-64", "65-74", "75+"]

def swap_within_groups(df, swap_ratio):
    df_swapped = df.copy()
    df_swapped["AGE_GROUP"] = pd.cut(df_swapped["AGE"], bins=BINS, labels=LABELS, right=True)

    for group, group_df in df_swapped.groupby("AGE_GROUP"):
        idx_all = group_df.index.tolist()

        # --- 1. GROUPED_COLS は同じペアでスワッピング ---
        idx = idx_all.copy()
        np.random.shuffle(idx)
        n_pairs = int(len(idx) * swap_ratio // 2)
        chosen = idx[: n_pairs * 2]

        for i in range(0, len(chosen), 2):
            idx1, idx2 = chosen[i], chosen[i+1]
            for col in GROUPED_COLS:
                val1, val2 = df_swapped.at[idx1, col], df_swapped.at[idx2, col]
                df_swapped.at[idx1, col], df_swapped.at[idx2, col] = val2, val1

        # --- 2. INDEPENDENT_COLS は列ごとに別ペアを作る ---
        for col in INDEPENDENT_COLS:
            idx = idx_all.copy()
            np.random.shuffle(idx)
            n_pairs = int(len(idx) * swap_ratio // 2)
            chosen = idx[: n_pairs * 2]

            for i in range(0, len(chosen), 2):
                idx1, idx2 = chosen[i], chosen[i+1]
                val1, val2 = df_swapped.at[idx1, col], df_swapped.at[idx2, col]
                df_swapped.at[idx1, col], df_swapped.at[idx2, col] = val2, val1

    return df_swapped.drop(columns=["AGE_GROUP"])

def main():
    if len(sys.argv) != 4:
        print("Usage: python swap_features.py <input_csv> <output_csv> <swap_ratio>")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    swap_ratio = float(sys.argv[3])

    # データ読み込み
    df = pd.read_csv(input_csv)

    # スワッピング実行
    df_swapped = swap_within_groups(df, swap_ratio)

    # 出力
    df_swapped.to_csv(output_csv, index=False)
    print(f"Swapped data saved to {output_csv} (swap_ratio={swap_ratio})")

if __name__ == "__main__":
    main()
