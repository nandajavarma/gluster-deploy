from setuptools import setup, find_packages

setup(
    name="gluster-deploy",

    version="1.0.0",

    author="Nandaja Varma",
    author_email="nandaja.varma@gmail.com",

    packages=[  'gluster-deploy',
                'gluster-deploy.lib',
                'gluster-deploy.modules',
                'gluster-deploy.bin'],

    include_package_data=True,

    url="https://github.com/nandajavarma/gluster-deploy",

    license="LICENSE",
    description="Useful towel-related stuff.",

    long_description=open("README").read(),

    install_requires=[
        "ansible",
        "pyyaml",
    ],
)
