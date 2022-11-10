pyuic5 -x .\gachaBotUI.ui -o .\gachaBotUI.py
pyrcc5 gachaBotUIResources.qrc -o gachaBotUIResources_rc.py

:: Then open gachaBotUI.py and change 'import gachaBotUIResources_rc' to 'import media.gachaBotUIResources_rc'