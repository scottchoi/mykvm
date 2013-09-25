import os.path

VERSION = "0.3.8"
BASE_IMAGES_PATH = os.getenv("HOME") + '/' + '.mykvm/base'
MYKVM_CONFIG_PATH = os.getcwd() + '/' + '.mykvm'
IMAGES_PATH = MYKVM_CONFIG_PATH + '/' + 'images'