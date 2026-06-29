from ase.io import read, write
from pathlib import Path

a = read("sio2/sio2_oh_initial.cif")
input_dir = Path("init_Cu_xyz")
output_dir = Path("sio2-cu-oh")
output_dir.mkdir(exist_ok=True)

gap = 2.0      # Cu团簇最低原子距离SiO2表面高度，Å
z_cell = 40.0  # 新的z轴晶胞长度，Å

for b_file in Path(input_dir).glob("*.xyz"):     

    b = read(b_file)

    # xy方向对齐到SiO2中心
    center_a = a.positions[:, 0:2].mean(axis=0)
    center_b = b.positions[:, 0:2].mean(axis=0)
    b.translate([center_a[0] - center_b[0], center_a[1] - center_b[1], 0])

    # z方向放到SiO2上方
    z_top_a = a.positions[:, 2].max()
    z_bottom_b = b.positions[:, 2].min()
    b.translate([0, 0, z_top_a - z_bottom_b + gap])

    merged = a + b

    cell = a.cell.copy()
    cell[2, 2] = z_cell
    merged.set_cell(cell, scale_atoms=False)
    merged.set_pbc(a.pbc)

    out_file = output_dir / f"sio2-{b_file.stem}.cif"
    write(out_file, merged)

    print("written:", out_file)