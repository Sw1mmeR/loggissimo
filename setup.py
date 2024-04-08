import loggissimo
from setuptools import setup, find_packages

setup(
    name=loggissimo.__name__,
    version=loggissimo.__version__,
    author="Sw1mmeR & AfanasevAndrey",
    description="Awesome and simple logger",
    packages=find_packages(),
    package_data={
        loggissimo.__name__: ["py.typed"],
    },
)
