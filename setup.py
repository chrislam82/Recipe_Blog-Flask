# To make installable:
#       Run
#pip install -e

from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='1.0.0',
    packages=find_packages(), # Automatically find all packages required/imported
    include_package_data=True, # So that we also look for files in MANIFEST.in to be included in package
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)

# MANIFEST.in contains all other files (e.g. static that are not included here)
#       E.g. style.css, templates, schema.sql

