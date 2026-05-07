"""PyInstaller 可执行文件的启动包装器。

双击运行后启动 Streamlit 服务器并自动打开浏览器。
"""

import sys
import os
import subprocess
import webbrowser
import time
import threading


def open_browser(port):
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{port}")


def main():
    port = 8501

    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    app_path = os.path.join(base_dir, "app.py")

    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            app_path,
            "--server.port",
            str(port),
            "--server.headless",
            "true",
            "--browser.serverAddress",
            "localhost",
        ]
    )


if __name__ == "__main__":
    main()
