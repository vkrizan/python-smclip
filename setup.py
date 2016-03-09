import codecs
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))


def get_version():
    init_file = os.path.join(here, 'smclip/__init__.py')
    with open(init_file) as f:
        for line in f:
            if line.startswith('__version__ = '):
                return eval(line.split('=')[-1])

with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='smclip',
    version=get_version(),
    description='Simple Multi Command Line Parser',
    long_description=long_description,
    url='https://github.com/vkrizan/python-smclip',
    author='Viliam Krizan',
    author_email='vkrizan (AT) redhat.com',
    license='LGPLv3+',
    keywords='cli, argument parser, multi commands',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Terminals',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=['smclip'],
    tests_require=['pytest', 'mock', 'pytest-cov']
)


