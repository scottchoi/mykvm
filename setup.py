from setuptools import setup

setup(
    name = "mykvm",
    version = "0.2.0",
    packages = ['mykvm'],
    install_requires = ['ansible>=1.2', 'pyyaml>=3.10'],

    # metadata for upload to PyPI
    author = "Scott Choi",
    author_email = "hho.choi@me.com",
    description = "mykvm is a vagrant like tool to create a kvm instances",
    license = "PSF",
    keywords = "kvm vmbuilder qemu-imge virt-install",
    url = "https://github.com/scottchoi/mykvm",  

    entry_points = {
        'console_scripts': [
            'mykvm=mykvm.main:main'
        ]
    }
)
