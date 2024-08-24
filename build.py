import PyInstaller.__main__

PyInstaller.__main__.run([
    "main.py",
    "-F",
    "--add-data=assets:assets",
    "-w"
])
