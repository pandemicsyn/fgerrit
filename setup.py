from setuptools import setup, find_packages

install_requires = []

version = "0.0.1"
name = "fgerrit"

setup(
    name = name,
    version = version,
    author = "Florian Hines",
    author_email = "syn@ronin.io",
    description = "git gerrit extension",
    license = "Apache License, (2.0)",
    keywords = "git gerrit",
    url = "http://github.com/pandemicsyn/fgerrit",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.6',
        ],
    install_requires=install_requires,
    scripts=['bin/git-fgerrit', 'bin/git-fg']
    )
