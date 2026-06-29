import os
from ase.io import read, write
from collections import Counter

input_dir = "./sio2-cu-oh-co2"
output_dir = "./sio2-cu-co2-data"
os.makedirs(output_dir, exist_ok=True)

# ===== 固定类型顺序（非常关键）=====
specorder = ["C", "Cu", "O", "Si","H"]

print("===== 批量转换开始 =====\n")

for file in os.listdir(input_dir):
    if file.endswith(".cif"):
        path = os.path.join(input_dir, file)

        try:
            atoms = read(path)

            # ===== 元素统计 =====
            symbols = atoms.get_chemical_symbols()
            count = Counter(symbols)

            # ===== 输出统计信息 =====
            print(f"文件: {file}")
            print(f"总原子数: {len(atoms)}")

            for elem in specorder:
                print(f"  {elem}: {count.get(elem, 0)}")

            # 如果有未定义元素，提醒
            extra_elems = set(count.keys()) - set(specorder)
            if extra_elems:
                print("⚠️ 未在 specorder 中定义的元素:", extra_elems)

            # ===== 写 LAMMPS data =====
            out_name = file.replace(".cif", ".data")
            out_path = os.path.join(output_dir, out_name)

            write(
                out_path,
                atoms,
                format="lammps-data",
                atom_style="atomic",
                specorder=specorder
            )

            print("转换完成:", out_name)
            print("-" * 40)

        except Exception as e:
            print(f"失败: {file} -> {e}")
            print("-" * 40)

print("\n===== 全部完成 =====")