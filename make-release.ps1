[Console]::Write("Enter the old name for the release:")
$old_release_name = [Console]::ReadLine()

Rename-Item build/debug-test/latest/ "build/debug-test/${old_release_name}"
Rename-Item build/release/latest/ "build/release/latest/${old_release_name}"

python -m nuitka regis-desktop.py --standalone --windows-icon-from-ico=assets/regis-icon.ico --include-package-data=selenium --output-dir=build/debug-test/latest --include-data-dir=assets=assets --include-data-dir=bare-installation=installation
python -m nuitka regis-desktop.py --standalone --windows-icon-from-ico=assets/regis-icon.ico --include-package-data=selenium --output-dir=build/release/latest --include-data-dir=assets=assets --include-data-dir=bare-installation=installation --disable-console

Remove-Item build/debug-test/latest/regis-desktop.build
Rename-Item build/debug-test/latest/regis-desktop.dist "build/debug-test/latest/Regis Desktop"

Remove-Item build/release/latest/regis-desktop.build
Rename-Item build/release/latest/regis-desktop.dist "build/release/latest/Regis Desktop"
