For building with pyInstaller:
First make sure you have Poetry so all dependencies are installed by the pyproject.toml file
Tutorial is here: https://kivyschool.com/installation/
Once poetry is installed:
    poetry update
    poetry shell
    cd to this folder
    to build backgroundsubtraction.py using the supplied .spec file:
        python -m PyInstaller Backsub.spec --clean
    to build for mac, go to main folder and use the spec files there:
        python -m PyInstaller BacksubMAC.spec --clean
    Mac spec files were built and used with the M1 Silicon chip.