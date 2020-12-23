from setuptools import setup, find_packages

setup(
    name="adfd",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=open("requirements.txt").readlines(),
    # This works also in dev mode: pip install -e '.[stats]'
    extras_require={"stats": ["matplotlib", "numpy", "pandas"]},
    entry_points=dict(console_scripts=["adfd=adfd.cli:main"]),
)
