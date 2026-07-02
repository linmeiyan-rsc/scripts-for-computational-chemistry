from pathlib import Path
import argparse
import subprocess
import sys


# 你的单个文件夹处理脚本名称
EXTRACT_SCRIPT = "extract-result-to-cp2k.py"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch run extract-result-to-cp2k.py in selected folders."
    )

    parser.add_argument(
        "--dir",
        required=True,
        help=(
            "要处理的文件夹。"
            "例如：--dir=dir1,dir2,dir3；"
            "如果要处理当前目录下所有一级子文件夹，用 --dir=*"
        ),
    )

    return parser.parse_args()


def get_target_dirs(dir_arg):
    """
    解析 --dir 参数。

    --dir=dir1,dir2
    --dir=*
    """

    current_dir = Path.cwd()

    if dir_arg.strip() == "*":
        dirs = sorted(
            p for p in current_dir.iterdir()
            if p.is_dir()
            and not p.name.startswith(".")
            and p.name != "__pycache__"
        )
    else:
        dirs = []
        for item in dir_arg.split(","):
            item = item.strip()
            if item:
                dirs.append(current_dir / item)

    if not dirs:
        raise RuntimeError("没有找到需要处理的文件夹。")

    valid_dirs = []

    for d in dirs:
        if not d.exists():
            print(f"[跳过] 文件夹不存在：{d}")
            continue

        if not d.is_dir():
            print(f"[跳过] 不是文件夹：{d}")
            continue

        valid_dirs.append(d)

    if not valid_dirs:
        raise RuntimeError("没有有效的文件夹可以处理。")

    return valid_dirs


def ask_frame_for_dir(folder):
    """
    逐个文件夹询问 frame。
    输入整数，例如 0、25、-1。
    直接回车表示使用 extract-result-to-cp2k.py 脚本内部默认 FRAME。
    """

    while True:
        value = input(
            f"\n请输入文件夹 [{folder.name}] 中要提取的 frame index "
            f"（0=第一帧，-1=最后一帧，直接回车=使用默认 FRAME）："
        ).strip()

        if value == "":
            return None

        try:
            return int(value)
        except ValueError:
            print("输入无效，请输入整数，例如 0、25、-1。")


def run_extract_script(folder, frame, extract_script_path):
    """
    在指定文件夹中运行 extract-result-to-cp2k.py。
    """

    cmd = [
        sys.executable,
        str(extract_script_path),
    ]

    if frame is not None:
        cmd.append(f"--frame={frame}")

    print("\n" + "=" * 70)
    print(f"正在处理文件夹：{folder}")
    if frame is None:
        print("使用 extract-result-to-cp2k.py 中的默认 FRAME")
    else:
        print(f"使用 frame index：{frame}")
    print("=" * 70)

    result = subprocess.run(
        cmd,
        cwd=folder,
    )

    if result.returncode != 0:
        print(f"[失败] 文件夹 {folder.name} 处理失败。")
        return False

    print(f"[完成] 文件夹 {folder.name} 处理完成。")
    return True


def main():
    args = parse_args()

    batch_script_dir = Path(__file__).resolve().parent
    extract_script_path = batch_script_dir / EXTRACT_SCRIPT

    if not extract_script_path.exists():
        raise FileNotFoundError(
            f"没有找到 {EXTRACT_SCRIPT}。\n"
            f"请确认 batch.py 和 {EXTRACT_SCRIPT} 放在同一个目录下。"
        )

    target_dirs = get_target_dirs(args.dir)

    print("将要处理以下文件夹：")
    for d in target_dirs:
        print(f"  - {d.name}")

    success_count = 0
    fail_count = 0

    for folder in target_dirs:
        frame = ask_frame_for_dir(folder)
        ok = run_extract_script(folder, frame, extract_script_path)

        if ok:
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 70)
    print("批量处理结束")
    print(f"成功：{success_count}")
    print(f"失败：{fail_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()