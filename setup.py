import os
from setuptools import find_packages
from distutils.core import setup


# User-friendly description from README.md
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = ""

requirements = [
    "alabaster",
    "appdirs==1.4.4",
    "APScheduler==3.8.1",
    "argh==0.31.2",
    "asgiref==3.8.1",
    "Babel==2.14.0",
    "beautifulsoup4==4.12.3",
    "bump2version==0.5.11",
    "certifi==2024.2.2",
    "charset-normalizer==3.3.2",
    "click==8.1.7",
    "coverage==4.5.4",
    "defusedxml==0.8.0rc2",
    "distlib==0.3.8",
    "Django==4.2.11",
    "django-apscheduler==0.6.0",
    "django-compat==1.0.15",
    "django4-background-tasks==1.2.9",
    "docutils==0.20.1",
    "entrypoints==0.3",
    "filelock==3.13.1",
    "flake8==3.7.8",
    "greenlet==3.0.3",
    "idna==3.6",
    "imagesize==1.4.1",
    "importlib_metadata==7.1.0",
    "Jinja2==3.0.0",
    "jira==3.6.0",
    "lxml==5.1.0",
    "Mako==1.3.2",
    "MarkupSafe==2.1.5",
    "mccabe==0.6.1",
    "multitasking==0.0.11",
    "mypy-extensions==1.0.0",
    "nh3==0.2.15",
    "numpy==1.21.0",
    "oauthlib==3.2.2",
    "packaging==24.0",
    "pandas==1.1.5",
    "pathspec==0.12.1",
    "pathtools==0.1.2",
    "pillow==10.2.0",
    "pkginfo==1.10.0",
    "platformdirs==4.2.0",
    "pluggy==0.13.1",
    "psycopg2-binary==2.8.6",
    "py==1.11.0",
    "pycodestyle==2.5.0",
    "pyflakes==2.1.1",
    "Pygments==2.17.2",
    "PyMySQL==1.1.0",
    "python-dateutil==2.9.0.post0",
    "pytz==2024.1",
    "PyYAML==6.0.1",
    "readme_renderer==43.0",
    "regex==2023.12.25",
    "requests==2.31.0",
    "requests-oauthlib==1.4.0",
    "requests-toolbelt==1.0.0",
    "schedule==1.2.1",
    "six==1.16.0",
    "snowballstemmer==2.2.0",
    "soupsieve==2.5",
    "Sphinx",
    "sphinxcontrib-applehelp",
    "sphinxcontrib-devhelp",
    "sphinxcontrib-htmlhelp",
    "sphinxcontrib-jsmath",
    "sphinxcontrib-qthelp",
    "sphinxcontrib-serializinghtml",
    "SQLAlchemy==2.0.28",
    "sqlparse==0.4.4",
    "toml==0.10.2",
    "tomli==2",
    "tox==3.14.0",
    "tqdm==4.66.2",
    "twine==1.14.0",
    "typing_extensions==4.10.0",
    "tzlocal==2.1",
    "urllib3==2.2.1",
    "virtualenv==20.25.1",
    "watchdog==0.9.0",
    "XlsxWriter==3.2.0",
    "yfinance==0.1.70",
    "zipp==3.18.1",
    "matplotlib==3.7.4"
]

setup(
    # Name of the package
    name="stock_collector",
    entry_points={"console_scripts": ["stock_collector = stockcollector.manage:main"]},
    # Packages to include into the distribution
    packages=find_packages("."),
    include_package_data=True,
    # Start with a small number and increase it with
    package_data={'': ['*.html'],
    },
    # every change you make https://semver.org
    version="1.0.0",
    # Chose a license from here: https: //
    # help.github.com / articles / licensing - a -
    # repository. For example: MIT
    license="",
    # Short description of your library
    description="",
    # Long description of your library
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Your name
    author="volkan akcora",
    # Your email
    author_email="volkan.eymir.akcora@deutsche-boerse.com",
    # Either the link to your github or to your website
    url="",
    # Link from which the project can be downloaded
    download_url="",
    # List of keywords
    keywords=[],
    # List of packages to install with this one
    install_requires=requirements,
    # https://pypi.org/classifiers/
    classifiers=[],
)
