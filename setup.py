from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='engraver',
    version='0.1.6',
    description='A tool for cutting Onyx',
    long_description=long_description,
    url='https://github.com/onyx-platform/engraver',
    author='Distributed Masonry',
    author_email='support@onyxplatform.org',
    license='Eclipse',
    install_requires=['boto', 'mako', 'prettytable', 'toposort', 'pyyaml'],
    packages=['src'],
    package_data={
        'src': ['src/args.json', 'src/ansible_template/*',
                'src/ansible_template/group_vars/*',
                'src/ansible_template/vars/cluster_vars/machine_profiles/*'],
    },
    entry_points={
        'console_scripts': [
            'engraver=src.engraver:main',
        ],
    },
    include_package_data = True,
)
