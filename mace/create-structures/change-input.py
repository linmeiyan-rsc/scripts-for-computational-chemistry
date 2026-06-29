import os

root_dir = "./run-dir"   # 所有计算目录的总目录

for folder in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder)

    if not os.path.isdir(folder_path):
        continue

    # ===== 找 .data 文件 =====
    data_file = None
    for f in os.listdir(folder_path):
        if f.endswith(".data"):
            data_file = f
            break

    if data_file is None:
        print(f"跳过（无data）: {folder}")
        continue

    # ===== 找 input 文件 =====
    input_path = os.path.join(folder_path, "input.lammps")

    if not os.path.exists(input_path):
        print(f"跳过（无input.lammps）: {folder}")
        continue

    # ===== 读取并修改 =====
    with open(input_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith("read_data"):
            new_line = f"read_data {data_file}\n"
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    # ===== 写回 =====
    with open(input_path, "w") as f:
        f.writelines(new_lines)

    print(f"完成: {folder} → {data_file}")