from setuptools import setup


with open('requirements.txt') as f:
    requirements = [l.strip() for l in f.readlines() if not l.startswith('#')]

setup(
    name='adfd-website-tools',
    description='tools and content to generate the ADFD website',
    version='0.8',
    license='BSD and CC BY-NC-SA 4.0',
    author='Oliver Bestwalter',
    author_email='forenmaster@adfd.org',
    long_description='',
    packages=['adfd'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    # This works also in dev mode: pip install -e '.['stats']'
    extras_require={'stats': ['matplotlib', 'numpy', 'pandas']},
    platforms='Unix',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points=dict(console_scripts=[
        'cnt=adfd.cli:main',
        'db=adfd.db.cli:main',
        'sibu=adfd.sitebuilder.cli:main',
    ]),
)
