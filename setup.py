from setuptools import setup


with open("requirements.txt") as f:
    requirements = [l.strip() for l in f.readlines() if not l.startswith('#')]

setup(
    name='adfd-website-tools',
    description='tools to generate content for the ADFD website',
    version='0.5',
    license='BSD',
    author='Oliver Bestwalter',
    author_email='forenmaster@adfd.org',
    long_description='',
    packages=['adfd'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
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
    ]),
)
