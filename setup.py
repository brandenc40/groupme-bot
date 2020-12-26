import os

from setuptools import setup

import groupme_bot


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name='groupme-bot',
    version=groupme_bot.__version__,
    description='A simple bot builder for GroupMe',
    url='https://github.com/brandenc40/groupme-bot',
    author=groupme_bot.__author__,
    author_email='brandencolen@gmail.com',
    license='MIT',
    packages=['groupme_bot'],
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    install_requires=[
        'APScheduler>=3.6',
        'requests>=2.25',
        'starlette>=0.14',
        'uvicorn>=0.13'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
