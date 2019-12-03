#!"C:\Users\ami fidele\PycharmProjects\xyzshopping\venv\Scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'mtnmomo==3.0.1','console_scripts','mtnmomo'
__requires__ = 'mtnmomo==3.0.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('mtnmomo==3.0.1', 'console_scripts', 'mtnmomo')()
    )
