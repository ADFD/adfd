from setuptools import setup


setup(
    name='adfd',
    packages=['adfd'],
    install_requires=[
        'cached-property==1.3.0',
        'flask==0.10.1',
        'frozen-flask==0.12',
        'mysqlclient==1.3.7',
        'plumbum==1.6.0',
        'pyphen==0.9.4',
        'sqlalchemy==1.0.10',
        'translitcodec==0.4.0',
        'typogrify==2.0.7',
    ],
    # This works also in dev mode: pip install -e '.['stats']'
    extras_require={'stats': ['matplotlib', 'numpy', 'pandas']},
    entry_points=dict(console_scripts=['adfd=adfd.cli:main']))
