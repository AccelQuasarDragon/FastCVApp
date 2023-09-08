For building with pyInstaller:
First make sure you have Poetry so all dependencies are installed by the pyproject.toml file
Tutorial is here: https://kivyschool.com/installation/
Once poetry is installed:
    poetry update
    poetry shell
    cd to this folder
    to build backgroundsubtraction.py using the supplied .spec file:
        python -m PyInstaller Backsub.spec --clean
    to build for mac, use the MAC spec files:
        python -m PyInstaller MAC_Backsub.spec --clean
    Mac spec files were built and used with the M1 silicon chip.