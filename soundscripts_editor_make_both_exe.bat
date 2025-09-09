ren "soundscripts_editor.py" "soundscripts_editor.pyw"

pyinstaller --onefile --name=soundscripts_editor --collect-all tksheet --collect-all tkinterdnd2 --icon=soundscripts_editor.ico soundscripts_editor.pyw

ren "soundscripts_editor.pyw" "soundscripts_editor.py"

pyinstaller --onefile --name=soundscripts_editor_dev --collect-all tksheet --collect-all tkinterdnd2 --icon=soundscripts_editor.ico soundscripts_editor.py

pause