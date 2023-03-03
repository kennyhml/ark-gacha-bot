py -m pip install ark-api -U
py -m pip install qtconfig -U

@echo off
echo Updating dependencies completed.
echo Attempting to update ling ling, (only works with git)...
git pull
pause