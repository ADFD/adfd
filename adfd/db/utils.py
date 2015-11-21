# -*- coding: utf-8 -*-
import logging

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from adfd import cst


log = logging.getLogger(__name__)


def generate_schema(writeToFile="schema.py"):
    # todo use https://github.com/google/yapf to format file
    engine = create_engine(cst.DB_URL)
    meta = MetaData()
    meta.reflect(bind=engine)
    imports = ("from sqlalchemy import Table\n"
               "from db_reflection.schema import Base\n\n\n")
    defs = [imports]
    for table in meta.tables.values():
        defs.append("class %s(Base):\n    __table__ = "
                    "Table(%r, Base.metadata, autoload=True)\n\n\n" %
                    (table.name, table.name))
    declText = "".join(defs)
    if writeToFile:
        with open(writeToFile, "w") as f:
            f.write(declText)
    else:
        print(declText)


def get_db_session():
    """":rtype: sqlalchemy.orm.session.Session"""
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    Session = sessionmaker()
    engine = create_engine(cst.DB_URL, echo=False)
    Session.configure(bind=engine)
    return Session()


DB_SESSION = get_db_session()

if __name__ == '__main__':
    generate_schema(writeToFile='')
