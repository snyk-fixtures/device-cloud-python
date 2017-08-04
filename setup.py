from setuptools import setup

setup(
	name='hdcpython',
	version='0.0.1',
	description='Python library for Wind River\'s Helix Device Cloud',
	author='Wind River Systems',
	author_email='',
	packages=['hdcpython', 'hdcosal'],
	install_requires=[
		'paho-mqtt', 
		'requests'
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
		'Programming Language :: Python :: 2 :: Only',
		'Operating System :: Microsoft :: Windows :: Windows 7',
		'Operating System :: POSIX :: Linux',
		'Topic :: Software Development :: Libraries :: Python Modules'
		]
	)
