"""Sets up package."""

import setuptools

setuptools.setup(
    name="test-package",
    version="0.0.1",
    author="renadvent",
    packages=["src/bot", "src/site", "src/common"],
    description="A discord bot",
    license="MIT",
    python_requires=">=3.8",
)
