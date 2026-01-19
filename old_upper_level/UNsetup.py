# https://stackoverflow.com/a/78003167

# Source - https://stackoverflow.com/a
# Posted by sinoroc, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-18, License - CC BY-SA 4.0

#!/usr/bin/env python3
import setuptools
from setuptools import find_packages, find_namespace_packages
# https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
setuptools.setup(
    name='fastcvapp',
    version='0.2.3',
    packages=['fastcvapp', 'fastcvapp.fastcvapp'],
    package_dir= {
        "fastcvapp":"fastcvapp"
    }


    # packages=find_packages(where='fastcvapp'),    
    # package_dir={
    #     "fastcvapp": "fastcvapp/fastcvapp"
    # },
    # include_package_data=True,
    # package_data={"": ["*.ttf"], "": ["*.task"]},
)
# setuptools.setup(
#     name='fastcvapp',
#     version='0.2.3',
#     packages=find_namespace_packages(where='fastcvapp'),    
#     package_dir={
#         '': 'fastcvapp',
#     },
#     include_package_data=True,
#     package_data={"": ["*.ttf"], "": ["*.task"]},
# )
