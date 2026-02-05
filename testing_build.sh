#!/bin/bash

printf "\n\nRUNNING APP TEST SCRIPTS.\n\n"

printf "\n\nTesting arm64 build for Apple Silicon users.\n"
printf "When app opens, exit application to continue test script.\n"
python3 -c "import platform; print('ARM build:', platform.machine())"
./dist/Ultrasound_Grader_arm64.app/Contents/MacOS/Ultrasound_Grader_arm64

printf "\n\nTesting x86 build on Rosetta for Intel processor users.\n"
printf "When app opens, exit application to continue test script.\n"
arch -x86_64 python3 -c "import platform; print('x86 build:', platform.machine())"
arch -x86_64 ./dist/Ultrasound_Grader_x86.app/Contents/MacOS/Ultrasound_Grader_x86

printf "\nTest script complete.\n"