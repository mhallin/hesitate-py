from setuptools import setup, find_packages

version = __import__('hesitate').__version__


setup(
    name='hesitate',
    version=version,
    description='A stochastic Design by Contract utility',
    url='https://github.com/mhallin/hesitate-py',

    author='Magnus Hallin',
    author_email='mhallin@gmail.com',

    license='BSD',

    packages=find_packages(exclude=['tests']),

    test_suite='tests.all_tests',
)
