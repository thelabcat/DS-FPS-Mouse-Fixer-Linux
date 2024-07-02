cp config.toml dist/
pyinstaller -F --add-data mousefixes:mousefixes DS_FPS_mousefix.pyw
rm -rf build
rm -f *.spec