from setuptools import setup


with open("requirements.txt") as f:
    requirements = [l.strip() for l in f.readlines() if not l.startswith('#')]

setup(
    name='ADFD Website Generator',
    description='Content and tools to build the ADFD website',
    version='0.1',
    license='BSD for tools and CC for content',
    author='ADFD',
    author_email='webmaster@adfd.org',
    long_description='',
    packages=['adfd'],
    include_package_data=True,
    zip_safe=False,
    platforms='Unix',
    # install_requires=requirements,  # todo use real packages when stable
    entry_points=dict(console_scripts=[
        'adfd=adfd.cli:main',
    ]),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
