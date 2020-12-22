import os
from setuptools import setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name='groupme-bot',
    version='0.1.0',
    description='A simple bot builder for GroupMe',
    url='https://github.com/brandenc40/groupme-bot',
    author='Branden Colen',
    author_email='brandencolen@anl.gov',
    license='MIT',
    packages=['groupme_bot'],
    long_description=read('README'),
    install_requires=[
        'flask',
        'waitress',
        'apscheduler',
        'requests'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)