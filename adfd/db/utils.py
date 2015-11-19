# -*- coding: utf-8 -*-
import logging
import os
from types import FunctionType, MethodType

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from adfd import cst

log = logging.getLogger(__name__)


def poa(o):
    value = obj_attr(o)
    try:
        print(value)
        return

    except:
        for enc in cst.ENC.ALL:
            try:
                print(value.encode(enc))
                return

            except:
                pass


_specialAttrNames = [
    "str", "repr", "dict", "doc", "class", "delattr", "format",
    "getattribute", "hash", "init", "module", "new", "reduce", "reduce_ex",
    "setattr", "sizeof", "subclasshook", "weakref"]


SIMPLE_OBJECTS = [str, list, tuple, dict, set, int, float]


def obj_attr(obj, hideString='', filterMethods=True, filterPrivate=True,
             sanitize=False, excludeAttrs=None, indent=0, objName=""):
    try:
        if any(isinstance(obj, t) for t in SIMPLE_OBJECTS):
            content = ("[simple obj_attr] %s (%s): %s" %
                       (objName or "(anon)", type(obj).__name__, str(obj)))
            return content

        return _obj_attr(
            obj, hideString, filterMethods, filterPrivate,
            sanitize, excludeAttrs, indent, objName)

    except:
        msg = "problems calling obj_attr"
        log.error(msg, exc_info=True)
        return msg


def _obj_attr(obj, hideString='', filterMethods=True, filterPrivate=True,
              sanitize=False, excludeAttrs=None, indent=0, objName=""):
    """show attributes of any object - generic representation of objects"""
    excludeAttrs = excludeAttrs or []
    names = dir(obj)
    for specialObjectName in _specialAttrNames:
        n = "__%s__" % (specialObjectName)
        if n in names:
            names.remove(n)
    if hideString:
        names = [n for n in names if hideString not in n]
    if filterPrivate:
        names = [n for n in names if not n.startswith('_')]
    out = []
    for name in sorted([d for d in names if d not in excludeAttrs]):
        try:
            attr = getattr(obj, name)
            attrType = type(attr)
            if attr is obj:
                continue  # recursion avoidance

            if filterMethods and (attrType in [FunctionType, MethodType]):
                continue

            if attrType in (FunctionType, MethodType):
                try:
                    value = attr.__doc__.split("\n")[0]
                except:
                    value = "<<func>>"
            else:
                value = str(attr).replace("\n", "\n|  ")
            out.append((name, attrType.__name__, value))
        except AssertionError as e:
            out.append(("[A] %s" % (name), e.__class__.__name__, e))

        except Exception as e:
            out.append(
                ("[E] %s" % (name), e.__class__.__name__, e))
    out = out or [(objName, str(type(obj)), repr(obj))]
    boundTo = "'%s' " % (objName) if objName else ""
    header = "|# %s%s (0x%X) #|" % (boundTo, type(obj).__name__, (id(obj)))
    numDashes = 40 - len(header) // 2
    out = (
        ["\n," + "-" * (numDashes - 1) + header + "-" * numDashes] +
        [_prepare_content(content) for content in out] +
        ["'" + "-" * 80])
    if sanitize:
        out = [o.replace('<', '(').replace('>', ')') for o in out]
    if indent:
        out = ["%s%s" % (" " * indent, o) for o in out]
    return os.linesep.join(out) + "\n  "
    # return os.linesep.join(out) + "\ncaller: %s" % (caller(10))


def _prepare_content(contentTuple):
    """add line breaks within an attribute line"""
    name, typeName, value = contentTuple
    pattern = "| %-30s %15s: %%s" % (name, typeName.rpartition(".")[-1])
    if not isinstance(value, str):
        value = str(value)

    if value.strip().startswith("| "):
        return pattern % (value)

    windowSize = 80
    firstLineLength = len(pattern) - 7
    curPos = windowSize - firstLineLength
    lines = [pattern % value[:curPos]]
    while True:
        curString = value[curPos:curPos + windowSize]
        if not curString:
            break

        lines.append("\n|    %s" % (curString))
        curPos += windowSize
    return "".join(lines)


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


def get_session():
    """":rtype: sqlalchemy.orm.session.Session"""
    Session = sessionmaker()
    Session.configure(bind=create_engine(cst.DB_URL, echo=False))
    return Session()


if __name__ == '__main__':
    generate_schema(writeToFile='')
