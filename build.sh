#!/bin/bash

rm -rf build dist

rm -rf venv_arm64
python3.10 -m venv venv_arm64
source venv_arm64/bin/activate
python -c "import platform; print('ARM build:', platform.machine())"
pip install --upgrade pip
pip install -r requirements.txt

pyinstaller src/code/main.py -D \
--name "Ultrasound_Grader_arm64" \
--add-data "src/app_resources/*:app_resources" \
--icon=src/app_resources/icons/ultrasoundastronaut.icns \
--windowed \
--clean

codesign --force --deep --sign - dist/Ultrasound_Grader_arm64.app
xattr -dr com.apple.quarantine dist/Ultrasound_Grader_arm64.app
codesign --verify --deep --strict --verbose=2 dist/Ultrasound_Grader_arm64.app

deactivate

rm -rf venv_x86
arch -x86_64 python3.10 -m venv venv_x86
source venv_x86/bin/activate
arch -x86_64 python -c "import platform; print('x86 build:', platform.machine())"
arch -x86_64 pip install --upgrade pip
arch -x86_64 pip install  -r requirements.txt

arch -x86_64 pyinstaller src/code/main.py -D \
--name "Ultrasound_Grader_x86" \
--add-data "src/app_resources/*:app_resources" \
--icon=src/app_resources/icons/ultrasoundastronaut.icns \
--windowed \
--clean

deactivate

codesign --force --deep --sign - dist/Ultrasound_Grader_x86.app
xattr -dr com.apple.quarantine dist/Ultrasound_Grader_x86.app
codesign --verify --deep --strict --verbose=2 dist/Ultrasound_Grader_x86.app