import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="downpour",
    version="0.0.1.a1",
    author="Peter Hanrahan",
    author_email="ptr@hnrhn.com",
    description="A library to allow command-line control of Deluge WebUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DownpourAPI/downpour-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
