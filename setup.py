from setuptools import setup


with open('requirements.txt') as f:
    requirements = [l.strip() for l in f.readlines() if not l.startswith('#')]

setup(
    name='adfd',
    packages=['adfd'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    # This works also in dev mode: pip install -e '.['stats']'
    extras_require={'stats': ['matplotlib', 'numpy', 'pandas']},
    entry_points=dict(console_scripts=[
        'cnt=adfd.cli:main',
        'db=adfd.db.cli:main',
        'sibu=adfd.sitebuilder.cli:main',
    ]))
