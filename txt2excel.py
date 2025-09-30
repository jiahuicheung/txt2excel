import os
import pandas as pd
from tqdm import tqdm

# ⚠️ 修改这里为你的txt文件夹路径
folder_path = r"example_txt"

# 输入想要提取的列号（1表示第一列）
cols_input = input("请输入要提取的列号（例如: 1,3,5 表示第1、3、5列）: ")
columns_to_extract = [int(c.strip()) - 1 for c in cols_input.split(",") if c.strip().isdigit()]

def detect_separator(file_path, encoding):
    """尝试自动检测分隔符"""
    with open(file_path, "r", encoding=encoding, errors="ignore") as f:
        first_line = f.readline().strip()
    if "," in first_line:
        return ","
    elif "\t" in first_line:
        return "\t"
    else:
        return r"\s+"   # 默认空格分隔

def read_txt(file_path):
    """尝试用多种编码读取"""
    for enc in ["utf-8", "gbk", "ansi", "utf-16"]:
        try:
            sep = detect_separator(file_path, enc)
            df = pd.read_csv(file_path, sep=sep, header=None, engine="python", encoding=enc)
            return df
        except Exception:
            continue
    raise ValueError("无法读取文件，请检查编码或文件内容。")

# 找到所有txt文件
txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]
total_files = len(txt_files)

if total_files == 0:
    print("❌ 未找到任何 .txt 文件，请检查文件夹路径。")
else:
    print(f"✅ 共找到 {total_files} 个 .txt 文件，开始处理...\n")

    for filename in tqdm(txt_files, desc="处理进度", unit="文件"):
        txt_path = os.path.join(folder_path, filename)

        try:
            # 读取文件
            df = read_txt(txt_path)
            df_selected = df.iloc[:, columns_to_extract]

            # 第一行保持原样文本
            first_row = df_selected.iloc[0:1, :].copy()

            # 从第二行开始处理：第一列文本，其余列数字
            if len(df_selected) > 1:
                rest_rows = df_selected.iloc[1:, :].copy()
                for col in rest_rows.columns[1:]:
                    rest_rows[col] = pd.to_numeric(rest_rows[col], errors="coerce")
                rest_rows.iloc[:, 0] = rest_rows.iloc[:, 0].astype(str)
                df_selected = pd.concat([first_row, rest_rows], ignore_index=True)

            # 保存为Excel
            excel_path = os.path.join(folder_path, filename.replace(".txt", ".xlsx"))
            df_selected.to_excel(excel_path, index=False, header=False)

        except Exception as e:
            print(f"\n❌ 文件 {filename} 处理失败: {e}")

    print("\n🎉 所有文件处理完成！")
