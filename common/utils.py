"""
共通ユーティリティ関数
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Any


def save_to_csv(
    data: List[Dict[str, Any]],
    output_path: str,
    encoding: str = "utf-8-sig"
) -> str:
    """
    データをCSVファイルに保存

    Input:
        data: データのリスト
        output_path: 出力ファイルパス
        encoding: エンコーディング（デフォルト: utf-8-sig for Excel）

    Output:
        str: 保存されたファイルのパス
    """
    if not data:
        print("保存するデータがありません。")
        return ""

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # すべてのキーを取得
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())

    fieldnames = sorted(list(all_keys))

    with open(output_path, "w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in data:
            row = {key: item.get(key, "") for key in fieldnames}
            writer.writerow(row)

    print(f"CSVファイルを保存しました: {output_path}")
    return str(output_path_obj.absolute())


def extract_price_number(price_str: str) -> float:
    """
    価格文字列から数値を抽出

    Input:
        price_str: 価格文字列（例: "10000円", "1万円"）

    Output:
        float: 価格の数値（円単位）
    """
    if not price_str:
        return 0.0

    # 数字と「万」「円」を抽出
    match = re.search(r'([0-9,]+)', price_str.replace(',', ''))
    if match:
        number = float(match.group(1))
        if '万' in price_str:
            number *= 10000
        return number
    return 0.0
