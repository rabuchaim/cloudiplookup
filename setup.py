import os, sys, shutil, codecs
from setuptools import setup
from setuptools.command.install import install
import shutil

target_directory = '/var/lib/cloudiplookup/'

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        if os.name == 'posix':
            os.makedirs(os.path.dirname(target_directory), exist_ok=True)
            shutil.copy2('cloudiplookup/cloudiplookup.dat.gz', target_directory)
            shutil.copy2('cloudiplookup/cloudiplookup.json', target_directory)

setup(
    name='cloudiplookup',
    version='1.0.6',
    description='Cloud IP Lookup is a Pure Python application and library for Python 3 to verify which cloud platform a given IP address belongs to (AWS, Azure, Cloudflare, DigitalOcean, Google Services/Cloud, JD Cloud and Oracle Cloud).',
    url='https://github.com/rabuchaim/cloudiplookup',
    author='Ricardo Abuchaim',
    author_email='ricardoabuchaim@gmail.com',
    maintainer='Ricardo Abuchaim',
    maintainer_email='ricardoabuchaim@gmail.com',
    project_urls={
        "Source Code": "https://github.com/rabuchaim/cloudiplookup/tree/main/cloudiplookup",
        "Issue Tracker": "https://github.com/rabuchaim/cloudiplookup/issues",
    },
    bugtrack_url='https://github.com/rabuchaim/cloudiplookup/issues',    
    license='MIT',
    packages=['cloudiplookup'],
    cmdclass={'install': CustomInstallCommand},    
    keywords=['cloudiplookup','cloud ip lookup','geoip','aws','azure','gcp','pure-python','purepython','pure python','oracle cloud','oci','digitalocean','digital ocean'],
    package_dir = {'cloudiplookup': 'cloudiplookup'},
    package_data={
        'cloudiplookup': ['cloudiplookup.py','cloudiplookup.dat.gz','cloudiplookup.json'],
    },
    scripts=[],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Internet',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',  
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    include_package_data=True,
    long_description=codecs.open("README.md","r","utf-8").read(),
    long_description_content_type='text/markdown',    
    entry_points={
        'console_scripts': [
            'cloudiplookup = cloudiplookup.cloudiplookup:main_function'
        ]
    },    
)
