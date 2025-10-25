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
    # ===================================
    # CORE DJANGO
    # ===================================
    "Django==4.2.11",
    "asgiref==3.8.1",
    "sqlparse==0.4.4",
    
    # ===================================
    # DATABASE
    # ===================================
    "psycopg2-binary==2.8.6",
    
    # ===================================
    # SCHEDULER (APScheduler)
    # ===================================
    "APScheduler==3.8.1",
    "django-apscheduler==0.6.0",
    "pytz==2024.1",
    "tzlocal==2.1",
    
    # ===================================
    # DATA PROCESSING
    # ===================================
    "pandas==2.0.3",           # Updated from 1.1.5
    "numpy==1.24.3",           # Updated from 1.23
    "python-dateutil==2.9.0.post0",
    
    # ===================================
    # STOCK DATA (yfinance with workarounds)
    # ===================================
    "yfinance==0.2.66",        # Stable version with workarounds
    
    # ===================================
    # HTTP & REQUESTS
    # ===================================
    "requests==2.31.0",
    "urllib3==2.2.1",
    "certifi==2024.2.2",
    "charset-normalizer==3.3.2",
    "idna==3.6",
    
    # ===================================
    # DATA SCIENCE (Optional - for ML features)
    # ===================================
    "scikit-learn==1.5.1",
    "scipy==1.13.1",
    
    
    # ===================================
    # UTILITIES
    # ===================================
    "six==1.16.0",
    "typing_extensions==4.10.0",
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
    # List of keywords, and try to iunstall it all
    keywords=[],
    # List of packages to install with this one
    install_requires=requirements,
    # https://pypi.org/classifiers/
    classifiers=[],
)