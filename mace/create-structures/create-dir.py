import os
import shutil

# ===== 路径设置 =====
data_dir = "./choose-data"          # 存放 .data 文件
template_dir = "./template_input"  # 模板输入文件夹
output_root = "./run-dir"             # 生成的新目录

os.makedirs(output_root, exist_ok=True)

# ===== 遍历所有 data 文件 =====
for file in os.listdir(data_dir):
    if file.endswith(".data"):

        data_path = os.path.join(data_dir, file)

        # ===== 文件夹名字（去掉 .data）=====
        folder_name = file.replace(".data", "")
        new_folder = os.path.join(output_root, folder_name)

        # ===== 复制模板文件夹 =====
        if os.path.exists(new_folder):
            print(f"已存在，跳过: {folder_name}")
            continue

        shutil.copytree(template_dir, new_folder)

        # ===== 复制 data 文件进去 =====
        shutil.copy(data_path, os.path.join(new_folder, file))

        print(f"完成: {folder_name}")