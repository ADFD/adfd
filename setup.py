from setuptools import setup

setup(
    name="adfd",
    packages=["adfd"],
    install_requires=open("requirements.txt").readlines(),
    # This works also in dev mode: pip install -e '.[stats]'
    extras_require={"stats": ["matplotlib", "numpy", "pandas"]},
    entry_points=dict(console_scripts=["adfd=adfd.cli:main"]),
)
