from setuptools import setup, find_packages

setup(
    name='gitlab-analytics',
    version='1.0',
    author='ndhw',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click==6.2',
    ],
    entry_points='''
        [console_scripts]
    ''',
)