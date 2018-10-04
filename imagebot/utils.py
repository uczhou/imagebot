import os
import hashlib


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def get_md5(item):
    return hashlib.sha1(item.encode('utf-8')).hexdigest()