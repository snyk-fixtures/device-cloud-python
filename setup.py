from setuptools import setup
import sys

pyver = sys.version_info

if pyver < (2,7,9) or (pyver > (3,0,0) and pyver < (3,4,0)):
    print("Sorry, your Python version ({}.{}.{}) is not supported by helix!".format(pyver[0], pyver[1], pyver[2]))
    sys.exit('Please upgrade to Python 2.7.9 or 3.4 and try again.')

setup(
    name='helix',
    version='17.08.16',
    description='Python library for Wind River\'s Helix Device Cloud',
    author='Wind River Systems',
    author_email='',
    packages=['helix','helix._core','helix.test'],
    install_requires=[
        'paho-mqtt',
        'requests',
        'certifi',
        'websocket-client'
        ],
    maintainer='Paul Barrette',
    maintainer_email='paul.barrette@windriver.com',
    url='http://www.windriver.com/products/helix/',
    license='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ]
    )
