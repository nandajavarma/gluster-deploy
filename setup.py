import sys
import os
import datetime
from setuptools import setup, find_packages

name='gluster-deploy'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README')
        + '\n'
        )

setup(
    name=name,
    version=datetime.datetime.now().strftime("%Y%m%d"),
    url='https://github.com/nandajavarma/gluster-deploy'
    license='AGPL 3.0',
    description='Gluster deployement automation tool using ansible',
    author='Nandaja Varma',
    author_email='nandaja.varma@gmail.com',
    long_description=long_description,
    include_package_data=True,
    packages=find_packages('gluster-deploy'),
    namespace_packages=['gluster-deploy'],
    install_requires=['setuptools', 'ansible', 'pyyaml'],
    zip_safe = True,
    )
