import setuptools

setuptools.setup(
    name="baumdiff",
    use_scm_version=True,
    author="Igor Podolskiy",
    author_email="igor.podolskiy@gmx.de",
    description="Tree Diff and Merge Library",
    packages=["baumdiff"],
    url="https://github.com/podolsir/baumdiff",
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
    ],
    setup_requires=['setuptools_scm'],
    install_requires=[],
    extras_require={
        'tests': ["pytest", "pytest-cov", "coverage"],
    },
    python_requires='>=3.3',
    
)