#!/usr/bin/env python3
"""
Setup script for Outlook Mail Automation
"""

from setuptools import setup, find_packages

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="outlook-mail-automation",
    version="1.0.0",
    author="Outlook Mail Automation Developer",
    author_email="developer@example.com",
    description="A Python-based automation tool for Microsoft Outlook email operations using Microsoft Graph API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/outlook-mail-automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Email",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "outlook-auth=get_refresh_token:main",
            "outlook-mail=mail_api:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "*.txt"],
    },
    keywords="outlook, email, automation, microsoft, graph, api, oauth2",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/outlook-mail-automation/issues",
        "Source": "https://github.com/yourusername/outlook-mail-automation",
        "Documentation": "https://github.com/yourusername/outlook-mail-automation/blob/main/README.md",
    },
) 