source bin/activate
pyinstaller src/code/main.py -D \
--name "Ultrasound_Grader_mac" \
--add-data "src/app_resources/*:app_resources" \
--icon=src/app_resources/icons/ultrasoundastronaut.icns \
--windowed \
--clean
