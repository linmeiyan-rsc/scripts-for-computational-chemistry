import os
import tkinter as tk
from tkinter import simpledialog

# ===== 根目录 =====
root_dir = "./run-dir"   # 改成你的目录

# ===== 创建 GUI =====
root = tk.Tk()
root.withdraw()  # 不显示主窗口

for folder in sorted(os.listdir(root_dir)):
    folder_path = os.path.join(root_dir, folder)

    if not os.path.isdir(folder_path):
        continue

    input_path = os.path.join(folder_path, "input.lammps")

    if not os.path.exists(input_path):
        print(f"跳过（无 input.lammps）: {folder}")
        continue

    # ===== 弹出输入框 =====
    temp = simpledialog.askstring(
        title="设置温度",
        prompt=f"结构: {folder}\n请输入温度 (K):"
    )

    # 用户取消
    if temp is None:
        print(f"已跳过: {folder}")
        continue

    # ===== 读取文件 =====
    with open(input_path, "r") as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        if line.strip().startswith("variable") and "TEMP" in line:
            # 替换温度
            new_line = f"variable        TEMP            equal {temp}\n"
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    # ===== 写回 =====
    with open(input_path, "w") as f:
        f.writelines(new_lines)

    print(f"完成: {folder} → TEMP = {temp}")

print("\n全部完成 ✅")