from setuptools import setup

import mykvm
import os

files = [(x[0], map(lambda y: x[0]+'/'+y, x[2])) for x in os.walk('ansible')]

setup(
    name = "mykvm",
    version = mykvm.VERSION,
    packages = ['mykvm'],
    install_requires = ['ansible>=1.2', 'pyyaml>=3.10'],
    data_files=[('conf', ['conf/mykvm.yml']), ('script', ['script/vmbuilder.sh'])] + files,

    # metadata for upload to PyPI
    author = "Scott Choi",
    author_email = "hho.choi@me.com",
    description = "mykvm is a vagrant like tool to create multiple kvm instances",
    license = "PSF",
    keywords = "kvm vmbuilder qemu-imge virt-install",
    url = "https://github.com/scottchoi/mykvm",  

    entry_points = {'console_scripts': ['mykvm=mykvm.main:main']}
)
