#!/bin/bash

rm -rf build dist
source venv_arm64/bin/activate

pyinstaller src/code/main.py -D \
--name "Ultrasound_Grader_arm64" \
--add-data "src/app_resources/*:app_resources" \
--icon=src/app_resources/icons/ultrasoundastronaut.icns \
--windowed \
--clean

deactivate

./dist/Ultrasound_Grader_arm64.app/Contents/MacOS/Ultrasound_Grader_arm64