from setuptools import setup, find_packages

setup(
    name='durc',
    description='Hierarchical CRUD utils for python projects',
    version='2.2.0',
    author='Filipe Alves',
    author_email='filipe.alvesdefernando@gmail.com',
    packages=find_packages(),
    install_requires=[
        'Cerberus',
    ],
    url='https://github.com/filipealvesdef/durc',
    zip_safe=False,
)
