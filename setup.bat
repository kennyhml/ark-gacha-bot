@echo off

:: check if python is installed
>nul 2>nul assoc .py

if errorlevel 1 (
    :: python is not installed
    echo Python not installed, downloading installer...
    powershell -c "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.1/python-3.11.1-amd64.exe' -OutFile '%USERPROFILE%\AppData\Local\Temp\python-3.11.1.exe'"
    echo Launching installer, please make sure to follow the correct setup instructions!
    echo:

    "%USERPROFILE%\AppData\Local\Temp\python-3.11.1.exe"
    pause
    echo Please press any button once you have completed the python setup, so we can continue installing the depedencies.

) else (
    echo Python is already installed. Please make sure its of version 3.10 or higher.
)

:: get depedencies, not worth checking worst case they are already installed.
echo Installing dependencies...
pip install -r requirements.txt

echo Finished installing dependencies.
echo: 


:: check if tesseract installer is already in temp, download if its not
if not exist "%USERPROFILE%\AppData\Local\Temp\tesseract.exe" (
    echo Downloading tesseract installer because it does not yet exist.
    powershell -c "Invoke-WebRequest -Uri 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.3.0.20221214.exe' -OutFile '%USERPROFILE%\AppData\Local\Temp\tesseract.exe'"
) else (
    echo Skipped downloading tesseract installer because it already exists.
)


:: check if we need to run the installer of if its already setup where it should be
if exist "C:\Program Files\Tesseract-OCR\" (
    echo Skipped executing installer because tesseract is already installed.

) else ("%USERPROFILE%\AppData\Local\Temp\tesseract.exe")


echo Setup finished.
pause