from ase.io import read, write
from ase import Atoms
from pathlib import Path
import numpy as np

input_dir = Path("sio2-cu-oh")
output_dir = Path("sio2-cu-oh-co2")
output_dir.mkdir(exist_ok=True)

gap = 2
bond = 1.16   # C=O 键长，Å

lon_deg = 0    # 经度角：xy平面内，从+x轴逆时针转
lat_deg = 90    # 纬度角：与+z轴夹角

lon = np.radians(lon_deg)
lat = np.radians(lat_deg)

direction = np.array([
    np.sin(lat) * np.cos(lon),
    np.sin(lat) * np.sin(lon),
    np.cos(lat)
])

for file in input_dir.glob("*.cif"):
    slab = read(file)

    center_xy = slab.positions[:, 0:2].mean(axis=0)
    center = np.array([center_xy[0], center_xy[1], 0.0])

    co2 = Atoms(
        "OCO",
        positions=[
            center - bond * direction,
            center,
            center + bond * direction,
        ]
    )

    z_top = slab.positions[:, 2].max()
    z_bottom = co2.positions[:, 2].min()
    co2.translate([0, 0, z_top - z_bottom + gap])

    merged = slab + co2
    merged.set_cell(slab.cell)
    merged.set_pbc(slab.pbc)

    new_name = f"{file.stem}-co2.cif"
    write(output_dir / new_name, merged)

    print(file.name, "->", new_name)