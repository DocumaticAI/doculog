import re

from setuptools import find_packages, setup


def get_version():
    result = re.search(
        r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', open("autolog/__init__.py").read()
    )
    return result.group(1)


setup(
    version=get_version(),
)
