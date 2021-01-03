from setuptools import setup, find_packages

# pyphen==0.9.4
# typogrify==2.0.7
requirements = [
    "boltons",
    "flask",
    "frozen-flask",
    "html5lib==0.999999999",
    "matplotlib",
    "mysqlclient",
    "pygments",
    "pyyaml",
    "sqlalchemy",
    "beautifulsoup4==4.5.1",
    "plumbum==1.6.3",
]

extras = {
    "stats": ["matplotlib", "numpy", "pandas"],
    "test": ["pytest"],
    "check_urls": ["async_timeout==2.0.1", "aiohttp==3.1.0"],
}
extras["all"] = requirements + extras["stats"] + extras["test"] + extras["check_urls"]

setup(
    name="adfd",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points=dict(console_scripts=["adfd=adfd.cli:main"]),
    install_requires=requirements,
    # This works also in dev mode: pip install -e '.[stats]'
    extras_require=extras,
)
