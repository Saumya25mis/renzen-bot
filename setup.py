"""Sets up package."""

import setuptools

setuptools.setup(
    name="test-package",
    version="0.0.1",
    author="renadvent",
    packages=["src"],
    description="A discord bot",
    license="MIT",
    # python_requires=">=3.8",
    install_requires=["boto3", "discord.py", "psycopg2"],
)
