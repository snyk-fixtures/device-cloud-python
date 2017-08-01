from distutils.core import setup

setup(
	name='hdcpython',
	version='1.0',
	description='Python library for Wind River\'s Helix Device Cloud',
	author='Wind River Systems',
	packages=['hdcpython', 'hdcosal'],
	install_requires=[
		'paho-mqtt', 
		'requests'
		]
	)
