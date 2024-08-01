import os
import shutil
import sys
import getpass

username = getpass.getuser()

PATH_LOCAL_TEMP = 'C:\\Users\\' + username + '\\AppData\\Local\\Temp'

if os.path.exists(PATH_LOCAL_TEMP) and not os.path.isfile(PATH_LOCAL_TEMP):
    shutil.rmtree(PATH_LOCAL_TEMP, ignore_errors=True)

sys.exit()