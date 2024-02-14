# setup.py

from setuptools import setup, find_packages
from setuptools.command.install import install
import os

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        user_home = os.path.expanduser('~')
        ipython_startup_path = os.path.join(user_home, '.ipython', 'profile_default', 'startup', 'ptipython_enhancer.py')
        with open(ipython_startup_path, 'w') as f:
            f.write("from ptipython_enhancer.utilities import *\n")
        print("ptipython utilities have been injected.")
        
setup(
    name='ptipython_enhancer',
    version='0.1',
    packages=find_packages(),
    cmdclass={
        'install': PostInstallCommand,
    },
    # include other metadata as needed
)
