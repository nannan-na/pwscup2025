# 0/1に変換前の確率をCSVに出力
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
xgbt_pred_proba.py — output probability predictions to CSV

- モデルJSONの version と実行中 xgboost のバージョンを比較し、古ければ明示エラーで終了
- attributes（最優先）/ learner.attributes / learner.feature_names を柔軟に読む
- feature_names が得られれば、test をその順で reindex（不足列0埋め・余分列削除）
- 各レコードの予測確率を CSV に1列で出力
"""

import argparse
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from typing import List, Optional, Tuple

# --------- version utils ---------
def ver_tuple_from_runtime(v: str) -> Tuple[int, int, int]:
    parts = []
    for tok in v.split("."):
        num = ""
        for ch in tok:
            if ch.isdigit():
                num += ch
            else:
                break
        if num:
            parts.append(int(num))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])

def ver_tuple_from_model(v) -> Tuple[int, int, int]:
    if isinstance(v, list) and len(v) >= 3:
        try:
            return (int(v[0]), int(v[1]), int(v[2]))
        except Exception:
            return (0, 0, 0)
    return (0, 0, 0)

# --------- schema extraction ---------
def extract_schema_flex(j: dict, cli_target: Optional[str]) -> tuple[Optional[List[str]], str]:
    attrs = j.get("attributes")
    if not isinstance(attrs, dict):
        attrs = j.get("learner", {}).get("attributes", {}) or {}

    feat: Optional[List[str]] = None
    fn_val = attrs.get("feature_names", None)
    if isinstance(fn_val, str):
        try:
            tmp = json.loads(fn_val)
            if isinstance(tmp, list) and all(isinstance(x, str) for x in tmp):
                feat = tmp
        except Exception:
            pass
    elif isinstance(fn_val, list) and all(isinstance(x, str) for x in fn_val):
        feat = fn_val
    if feat is None:
        lf = j.get("learner", {}).get("feature_names")
        if isinstance(lf, list) and all(isinstance(x, str) for x in lf) and len(lf) > 0:
            feat = lf

    target = cli_target or attrs.get("target") or "stroke_flag"
    return feat, target

# --------- preprocessing ---------
def build_X(df: pd.DataFrame, target: Optional[str]) -> pd.DataFrame:
    cols_drop = [c for c in [target] if c and c in df.columns]
    X_raw = df.drop(columns=cols_drop, errors="ignore").copy()

    X_num_try = X_raw.apply(pd.to_numeric, errors="coerce")
    num_cols = [c for c in X_num_try.columns if X_num_try[c].notna().sum() > 0]
    X_num = X_num_try[num_cols] if num_cols else pd.DataFrame(index=df.index)

    cat_cols = [c for c in X_raw.columns if c not in num_cols]
    X_cat = (pd.get_dummies(X_raw[cat_cols].astype("category"), drop_first=True)
             if cat_cols else pd.DataFrame(index=df.index))

    X = pd.concat([X_num, X_cat], axis=1)
    X = X.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    X = X.dropna(axis=1, how="all")
    if X.shape[1] == 0:
        raise SystemExit("No usable features after preprocessing.")

    zero_var = X.nunique(dropna=False) <= 1
    if zero_var.all():
        raise SystemExit("All feature columns have zero variance.")
    if zero_var.any():
        X = X.loc[:, ~zero_var]

    X = X.reindex(columns=sorted(X.columns))
    return X.astype("float32")

# --------- main ---------
def main():
    ap = argparse.ArgumentParser(description="Predict with trained XGBoost JSON model and output probabilities to CSV.")
    ap.add_argument("model_json", help="trained model JSON (Booster.save_model)")
    ap.add_argument("--test-csv", required=True, help="test CSV with header")
    ap.add_argument("--target", default=None, help="target column name (override model metadata)")
    ap.add_argument("--output-csv", required=True, help="出力先のCSVファイル名")
    args = ap.parse_args()

    # モデルJSON 読み
    with open(args.model_json, "r", encoding="utf-8") as f:
        j = json.load(f)

    # バージョン整合チェック
    model_ver = ver_tuple_from_model(j.get("version"))
    runtime_ver = ver_tuple_from_runtime(xgb.__version__)
    if model_ver > runtime_ver:
        mv = ".".join(map(str, model_ver))
        rv = ".".join(map(str, runtime_ver))
        raise SystemExit(
            f"xgboost runtime ({rv}) はモデルのバージョン ({mv}) より古く、JSON を読み込めません。\n"
            f"→ `python3 -m pip install --user --upgrade \"xgboost=={mv}\"` で更新するか、"
            f"同じ/古いバージョンでモデルを書き出してください。"
        )

    feature_names_model, target = extract_schema_flex(j, args.target)

    # テストCSV読み込み
    df_te = pd.read_csv(args.test_csv, dtype=str, keep_default_na=False)
    if target not in df_te.columns:
        raise SystemExit(f"Target column '{target}' not found in test CSV.")

    X_te = build_X(df_te, target=target)

    if feature_names_model:
        for col in feature_names_model:
            if col not in X_te.columns:
                X_te[col] = 0.0
        X_te = X_te.reindex(columns=feature_names_model)

    booster = xgb.Booster()
    booster.load_model(args.model_json)

    if feature_names_model:
        dtest = xgb.DMatrix(X_te, feature_names=feature_names_model)
    else:
        dtest = xgb.DMatrix(X_te)

    # 各レコードの確率を予測
    proba = booster.predict(dtest, validate_features=True)

    # 確率を1列のCSVに保存
        # 確率を1列のCSVに保存（ヘッダーなし）
    df_out = pd.DataFrame(proba)
    df_out.to_csv(args.output_csv, index=False, header=False)
    print(f"Saved probabilities to {args.output_csv} ({df_out.shape[0]} rows, no header)")

if __name__ == "__main__":
    main()
