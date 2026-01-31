# Full path to Python where PyInstaller is installed
$pythonPath = "C:\Users\Dima\AppData\Local\Python\pythoncore-3.14-64\python.exe"

# Build MCStatus EXE
& $pythonPath -m pyinstaller --onefile --name MCStatus MCServerStatus/MC_Server_Status/MCStatus.py

# Build Panel/WebStatus EXE
& $pythonPath -m pyinstaller --onefile --name PanelServerStatus MCServerStatus/Web_Server_Status/WebStatus.py

# Optional: show where the EXEs are
Write-Host "MCStatus.exe and PanelServerStatus.exe built in the 'dist' folder"
