[Console]::Write("Enter the name for the old release: ")
$old_release_name = [Console]::ReadLine()

Rename-Item -Path build/debug-test/latest/ -NewName $old_release_name
Rename-Item -Path build/release/latest/ -NewName $old_release_name

mkdir build/debug-test/latest/
mkdir build/release/latest/

python -m nuitka regis-desktop.py --standalone --windows-icon-from-ico=assets/regis-icon.ico --include-package-data=selenium --output-dir=build/debug-test/latest --include-data-dir=assets=assets --include-data-dir=bare-installation=installation
python -m nuitka regis-desktop.py --standalone --windows-icon-from-ico=assets/regis-icon.ico --include-package-data=selenium --output-dir=build/release/latest --include-data-dir=assets=assets --include-data-dir=bare-installation=installation --disable-console

Remove-Item build/debug-test/latest/regis-desktop.build -Recurse
Rename-Item -Path build/debug-test/latest/regis-desktop.dist/regis-desktop.exe -NewName Regis.exe
Rename-Item -Path build/debug-test/latest/regis-desktop.dist -NewName "Regis Desktop"


Remove-Item build/release/latest/regis-desktop.build -Recurse
Rename-Item -Path build/release/latest/regis-desktop.dist/regis-desktop.exe -NewName Regis.exe
Rename-Item -Path build/release/latest/regis-desktop.dist -NewName "Regis Desktop"
