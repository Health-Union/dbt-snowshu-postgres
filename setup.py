#!/usr/bin/env python
import os
import sys

package_name = "dbt-snowshu-postgres"
package_version = "0.19.0"
description = """The snowshu postgres adapter plugin for dbt (data build tool)"""


if sys.version_info < (3, 6):
    print('Error: %s does not support this version of Python.' % package_name)
    print('Please upgrade to Python 3.6 or higher.')
    sys.exit(1)


from setuptools import setup
try:
    from setuptools import find_namespace_packages
except ImportError:
    # the user has a downlevel version of setuptools.
    print('Error: %s requires setuptools v40.1.0 or higher.' % package_name)
    print('Please upgrade setuptools with "pip install --upgrade setuptools" '
          'and try again')
    sys.exit(1)


file_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(file_dir, "README.md")) as f:
    long_description = f.read()

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Health Union - Data Team",
    author_email="data@health-union.com",
    url="https://github.com/Health-Union/dbt-snowshu-postgres",
    packages=find_namespace_packages(include=['dbt', 'dbt.*']),
    package_data={
        'dbt': [
            'include/snowshupostgres/macros/*.sql',
            'include/snowshupostgres/macros/**/*.sql',
            'include/snowshupostgres/dbt_project.yml',
        ]
    },
    install_requires=[
        f"dbt-core=={package_version}",
        f"dbt-postgres=={package_version}",
    ]
)
