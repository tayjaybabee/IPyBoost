# post_install.py

import os

def post_install():
    user_home = os.path.expanduser('~')
    ipython_startup_path = os.path.join(user_home, '.ipython', 'profile_default', 'startup', 'ptipython_enhancer.py')
    with open(ipython_startup_path, 'w') as f:
        f.write("from ptipython_enhancer.utilities import *\n")
    print("ptipython utilities have been injected.")

if __name__ == "__main__":
    post_install()
