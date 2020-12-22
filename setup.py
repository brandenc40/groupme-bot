from setuptools import setup

setup(
    name='groupme-bot',
    version='0.1.0',
    description='A simple bot builder for GroupMe',
    url='https://github.com/brandenc40/groupme-bot',
    author='Branden Colen',
    author_email='brandencolen@anl.gov',
    license='MIT',
    packages=['groupme_bot'],
    install_requires=[
        'flask'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)