from pathlib import Path
import argparse
from ase.io import read, write


# =========================
# 默认设置
# =========================

LAMMPS_DUMP = None
# None 表示自动寻找当前文件夹下唯一的 xxxk.lammpstrj 文件
# 如果想手动指定，也可以写成：
# LAMMPS_DUMP = "400k.lammpstrj"

DUMP_PATTERN = "*k.lammpstrj"

FRAME = 25
# 默认帧数
# -1 表示最后一帧；0 表示第一帧
# 命令行输入 --frame=xxx 时，会覆盖这里的默认值

# LAMMPS type -> element
TYPE_MAP = ["C", "Cu", "O", "Si", "H"]

# 要提取的 LAMMPS atom id
# 如果想全部输出，就写成 []
SELECT_INDEX = []

OUTPUT_DIR = "input"
COORD_XYZ = "coord.xyz"
CELL_INC = "cell.inc"

PERIODIC = "XYZ"


# =========================
# 下面一般不需要改
# =========================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract one frame from a LAMMPS trajectory and write coord.xyz and cell.inc."
    )

    parser.add_argument(
        "--frame",
        type=int,
        default=FRAME,
        help=f"要读取的轨迹帧 index。0 表示第一帧，-1 表示最后一帧。默认值为脚本中的 FRAME={FRAME}",
    )

    return parser.parse_args()


def find_single_lammps_dump(folder=".", pattern="*k.lammpstrj"):
    """
    自动寻找当前文件夹下唯一的 LAMMPS 轨迹文件。

    优先寻找 xxxk.lammpstrj，例如：
    300k.lammpstrj
    400k.lammpstrj
    500k.lammpstrj

    如果没找到，再寻找任意 .lammpstrj 文件。
    """

    folder = Path(folder)

    files = sorted(folder.glob(pattern))

    if len(files) == 0:
        files = sorted(folder.glob("*.lammpstrj"))

    if len(files) == 0:
        raise FileNotFoundError(
            f"当前文件夹 {folder.resolve()} 中没有找到 .lammpstrj 文件"
        )

    if len(files) > 1:
        file_list = "\n".join(str(f) for f in files)
        raise RuntimeError(
            "当前文件夹中找到多个 .lammpstrj 文件，无法自动判断使用哪一个：\n"
            f"{file_list}\n\n"
            "请删除多余文件，或手动设置 LAMMPS_DUMP。"
        )

    return files[0]


def get_lammps_ids_in_frame(filename, frame=-1):
    """
    读取指定帧中 LAMMPS atom id 的顺序。
    用于把 SELECT_INDEX 里的 LAMMPS atom id 转成 ASE 的原子下标。
    """

    if frame < -1:
        raise ValueError("FRAME 只支持 -1 或 >=0 的整数")

    current_frame = -1
    last_ids = None

    with open(filename, "r") as f:
        while True:
            line = f.readline()

            if not line:
                break

            if not line.startswith("ITEM: TIMESTEP"):
                continue

            current_frame += 1

            # timestep
            f.readline()

            # number of atoms
            line = f.readline()
            if not line.startswith("ITEM: NUMBER OF ATOMS"):
                raise RuntimeError("没有找到 ITEM: NUMBER OF ATOMS")

            natoms = int(f.readline().strip())

            # box
            line = f.readline()
            if not line.startswith("ITEM: BOX BOUNDS"):
                raise RuntimeError("没有找到 ITEM: BOX BOUNDS")

            for _ in range(3):
                f.readline()

            # atom header
            line = f.readline()
            if not line.startswith("ITEM: ATOMS"):
                raise RuntimeError("没有找到 ITEM: ATOMS")

            columns = line.split()[2:]

            if "id" not in columns:
                raise RuntimeError("轨迹文件中没有 id 列，无法根据 LAMMPS atom id 提取")

            id_col = columns.index("id")

            ids = []
            for _ in range(natoms):
                parts = f.readline().split()
                ids.append(int(parts[id_col]))

            if frame >= 0 and current_frame == frame:
                return ids

            last_ids = ids

    if frame == -1:
        return last_ids

    raise IndexError(f"FRAME={frame} 超出轨迹帧数")


def write_cell_inc(atoms, filename, periodic="XYZ"):
    cell = atoms.get_cell()

    with open(filename, "w") as f:
        f.write("&CELL\n")
        f.write(f"  A [angstrom] {cell[0, 0]:16.8f} {cell[0, 1]:16.8f} {cell[0, 2]:16.8f}\n")
        f.write(f"  B [angstrom] {cell[1, 0]:16.8f} {cell[1, 1]:16.8f} {cell[1, 2]:16.8f}\n")
        f.write(f"  C [angstrom] {cell[2, 0]:16.8f} {cell[2, 1]:16.8f} {cell[2, 2]:16.8f}\n")
        f.write(f"  PERIODIC {periodic}\n")
        f.write("&END CELL\n")


def main():
    args = parse_args()
    frame = args.frame

    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    coord_file = output_dir / COORD_XYZ
    cell_file = output_dir / CELL_INC

    # 自动确定 LAMMPS dump 文件
    if LAMMPS_DUMP is None:
        lammps_dump = find_single_lammps_dump(".", DUMP_PATTERN)
    else:
        lammps_dump = Path(LAMMPS_DUMP)

    print(f"Using LAMMPS dump file: {lammps_dump}")
    print(f"Using frame index: {frame}")

    # 读取 LAMMPS dump
    atoms = read(
        lammps_dump,
        index=frame,
        format="lammps-dump-text",
        specorder=TYPE_MAP,
        order=False,
    )

    # 如果轨迹文件里有 type 信息，则再次强制映射元素
    if "type" in atoms.arrays:
        symbols = [TYPE_MAP[int(t) - 1] for t in atoms.arrays["type"]]
        atoms.set_chemical_symbols(symbols)

    # 根据 LAMMPS atom id 提取指定原子
    if SELECT_INDEX:
        frame_ids = get_lammps_ids_in_frame(lammps_dump, frame)
        id_to_ase_index = {atom_id: i for i, atom_id in enumerate(frame_ids)}

        ase_indices = []
        for atom_id in SELECT_INDEX:
            if atom_id not in id_to_ase_index:
                raise ValueError(f"LAMMPS atom id {atom_id} 不在这一帧里")
            ase_indices.append(id_to_ase_index[atom_id])

        atoms = atoms[ase_indices]

    # 输出 CP2K 可读 xyz
    write(coord_file, atoms, format="xyz")

    # 输出 cell.inc
    write_cell_inc(atoms, cell_file, periodic=PERIODIC)

    print("Done.")
    print(f"Written: {coord_file}")
    print(f"Written: {cell_file}")
    print(f"Number of atoms: {len(atoms)}")
    print(f"Type map: {TYPE_MAP}")


if __name__ == "__main__":
    main()