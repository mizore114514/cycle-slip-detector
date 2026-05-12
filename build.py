"""PyInstaller 打包脚本。

用法:
    python build.py          # 正常打包
    python build.py --run     # 打包后直接运行
"""

import subprocess
import sys
import platform
import os


def build():
    project_dir = os.path.dirname(os.path.abspath(__file__))

    system = platform.system()
    if system == "Windows":
        sep = ";"
        ext = ".exe"
    else:
        sep = ":"
        ext = ""

    name = "周跳探测"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        name,
        "--add-data",
        f"core{sep}core",
        "--add-data",
        f"ui{sep}ui",
        "--add-data",
        f"app.py{sep}.",
        "--hidden-import",
        "georinex",
        "--hidden-import",
        "plotly.express",
        "--hidden-import",
        "pandas",
        "--hidden-import",
        "streamlit",
        "--collect-all",
        "streamlit",
        "--collect-all",
        "plotly",
        str(os.path.join(project_dir, "run_app.py")),
    ]

    print(f">>> {' '.join(cmd)}")
    subprocess.check_call(cmd)
    print(f"\n=== 打包完成 ===")
    print(f"可执行文件: dist/{name}{ext}")


if __name__ == "__main__":
    build()
