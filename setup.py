###########################################################
#                      Journal Writer
#
#         A Borja Glez. Seoane's ad-hoc utility to
#                   write his Cartapacio
#
# Copyright 2022 Borja González Seoane. All rights reserved
###########################################################

# WARNING: Private tool. Won't be available since PyPI, but only since private
# repository

import setuptools

import journal_writer

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name=journal_writer.__name__,
    version=journal_writer.__version__,
    packages=["journal_writer"],
    entry_points={
        "console_scripts": [
            "jw = journal_writer.__main__:main",
        ],
    },
    python_requires=">=3.9",
    install_requires=requirements,
    data_files=[
        ("", ["requirements.txt"]),
        ("", ["README.md"]),
    ],
    url="https://github.com/bglezseoane/journal_writer",
    download_url=f"https://github.com/bglezseoane/journal_writer/archive/{journal_writer.__version__}.tar.gz",
    license=journal_writer.__license__,
    author=journal_writer.__author__,
    author_email=journal_writer.__email__,
    description=journal_writer.__desc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
