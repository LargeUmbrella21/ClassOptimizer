Executable and CBC
The executable was too big, so heres the command to run it (must have libraries installed)
python -m PyInstaller --onefile --hidden-import=pandas --hidden-import=tkinter --hidden-import=collections --hidden-import=pulp --add-binary="C:/Path/to/cbc.exe;." SpreadIMPORT2.py 
If the cbc.exe is not added to same dist, then manually copy and paste it into same directory as executable
