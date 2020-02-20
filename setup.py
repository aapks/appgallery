import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="appgallery-healplease", # Replace with your own username
    version="0.1.1",
    author="healplease",
    author_email="gavaalex2012@gmail.com",
    description="High-level API for interacting with Huawei AppGallery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/healplease/appgallery",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)