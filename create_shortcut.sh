#! /bin/bash
echo "[Desktop Entry]
Type=Application
Terminal=true
Exec=python3 `pwd`/main.py
Name=Microscope-Control
Comment=microscope
Encoding=UTF-8
Categories=Utility;
Icon=`pwd`/icon.png" > ~/Desktop/microscope.desktop
chmod +x ~/Desktop/microscope.desktop