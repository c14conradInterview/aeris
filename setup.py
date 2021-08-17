from setuptools import setup, find_packages


setup(name='aeris',
      version='1.0',
      description='Interview problem',
      author='Charles Conrad',
      packages=find_packages(),
      install_requires=['aerisweather=<0.4.1'],
     )