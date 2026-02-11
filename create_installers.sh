mkdir ./installers/arm64_installer/
mkdir ./installers/x86_installer/

cp ./src/app_resources/README.txt ./installers/arm64_installer/README.txt
cp -R ./dist/Ultrasound_Grader_arm64.app "./installers/arm64_installer/Ultrasound Grader (Apple Silicon).app"
ln -s /Applications ./installers/arm64_installer/Applications

cp ./src/app_resources/README.txt ./installers/x86_installer/README.txt
cp -R ./dist/Ultrasound_Grader_x86.app "./installers/x86_installer/Ultrasound Grader (Intel).app"
ln -s /Applications ./installers/x86_installer/Applications

hdiutil create \
  -volname "Ultrasound Grader Installer (Apple Silicon)" \
  -srcfolder ./installers/arm64_installer \
  -ov \
  -format UDZO \
  ./installers/arm64_installer/Ultrasound_Grader_Installer_arm64.dmg

hdiutil create \
  -volname "Ultrasound Grader Installer (Intel)" \
  -srcfolder ./installers/x86_installer/ \
  -ov \
  -format UDZO \
  ./installers/x86_installer/Ultrasound_Grader_Installer_x86.dmg

codesign --sign - ./installers/arm64_installer/Ultrasound_Grader_Installer_arm64.dmg
codesign --sign - ./installers/x86_installer/Ultrasound_Grader_Installer_x86.dmg

codesign --verify --deep --strict --verbose=2 ./installers/arm64_installer/Ultrasound_Grader_Installer_arm64.dmg
codesign --verify --deep --strict --verbose=2 ./installers/x86_installer/Ultrasound_Grader_Installer_x86.dmg