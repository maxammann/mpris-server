from setuptools import setup

setup(
    name='mpris-server',
    version='0.1',
    packages=["mpris"],
    url='',
    license='',
    author='max',
    author_email='',
    description='',
    install_requires=['flask',
                      'pympris',
                      'tornado'],
    scripts=['scripts/mpris_server'],
    include_package_data=True,
)
