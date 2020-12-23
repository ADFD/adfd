import logging
import os
from types import FunctionType, MethodType

log = logging.getLogger(__name__)

_specialAttrNames = [
    "str",
    "repr",
    "dict",
    "doc",
    "class",
    "delattr",
    "format",
    "getattribute",
    "hash",
    "init",
    "module",
    "new",
    "reduce",
    "reduce_ex",
    "setattr",
    "sizeof",
    "subclasshook",
    "weakref",
]
SIMPLE_OBJECTS = [str, list, tuple, dict, set, int, float]


def obj_attr(
    obj,
    hideString="",
    filterMethods=True,
    filterPrivate=True,
    sanitize=False,
    excludeAttrs=None,
    indent=0,
    objName="",
    terminalSize=100,
    maxLen=250,
):
    try:
        if any(isinstance(obj, t) for t in SIMPLE_OBJECTS):
            return "[{}] {} = {}".format(
                type(obj).__name__, objName or "(anon)", str(obj)
            )

        return _obj_attr(
            obj,
            hideString,
            filterMethods,
            filterPrivate,
            sanitize,
            excludeAttrs,
            indent,
            objName,
            terminalSize,
            maxLen,
        )

    except Exception as e:
        msg = "problems calling obj_attr"
        log.warning(f"{msg} of {obj}: {e}")
        log.error(msg, exc_info=True)
        return msg


def _obj_attr(
    obj,
    hideString,
    filterMethods,
    filterPrivate,
    sanitize,
    excludeAttrs,
    indent,
    objName,
    terminalSize,
    maxLen,
):
    """show attributes of any object - generic representation of objects"""
    excludeAttrs = excludeAttrs or []
    names = dir(obj)
    for specialObjectName in _specialAttrNames:
        n = "__%s__" % specialObjectName
        if n in names:
            names.remove(n)
    if hideString:
        names = [n for n in names if hideString not in n]
    if filterPrivate:
        names = [n for n in names if not n.startswith("_")]
    out = []
    maxTypeLen = 0
    for name in sorted([d for d in names if d not in excludeAttrs]):
        try:
            attr = getattr(obj, name)
            attrType = type(attr)
            if len(attrType.__name__) > maxTypeLen:
                maxTypeLen = len(attrType.__name__)
            if attr is obj:
                continue  # recursion avoidance

            if filterMethods and (attrType in [FunctionType, MethodType]):
                continue

            if attrType in (FunctionType, MethodType):
                try:
                    value = attr.__doc__.split("\n")[0]
                except Exception:
                    value = "<<func>>"
            else:
                value = str(attr).replace("\n", "\n|  ")
                if len(value) > maxLen:
                    value = value[:maxLen] + "[...]"
            out.append((name, attrType.__name__, value))
        except AssertionError as e:
            out.append(("[A] %s" % name, e.__class__.__name__, e))

        except Exception as e:
            out.append(("[E] %s" % name, e.__class__.__name__, e))
    out = out or [(objName, str(type(obj)), repr(obj))]
    boundTo = "'%s' " % objName if objName else ""
    header = "|# {}{} (0x{:X}) #|".format(boundTo, type(obj).__name__, (id(obj)))
    numDashes = (terminalSize // 2) - len(header) // 2
    maxNameLen = max([len(name) for name in names])
    out = (
        ["\n," + "-" * (numDashes - 1) + header + "-" * numDashes]
        + [_prep_line(content, maxNameLen, maxTypeLen, terminalSize) for content in out]
        + ["'" + "-" * terminalSize]
    )
    if sanitize:
        out = [o.replace("<", "(").replace(">", ")") for o in out]
    if indent:
        out = ["{}{}".format(" " * indent, o) for o in out]
    return os.linesep.join(out)


def _prep_line(contentTuple, maxNameLen, maxTypeLen, terminalSize):
    """add line breaks within an attribute line"""
    name, typeName, value = contentTuple
    typeName = typeName.rpartition(".")[-1]
    formattedName = name + " " * (maxNameLen - len(name))
    formattedType = typeName + " " * (maxTypeLen - len(typeName))
    pattern = f"| [{formattedType}] {formattedName} %s"
    if not isinstance(value, str):
        value = str(value)

    if value.strip().startswith("| "):
        return pattern % value

    windowSize = terminalSize
    firstLineLength = len(pattern) - 7
    curPos = windowSize - firstLineLength
    lines = [pattern % value[:curPos]]
    while True:
        curString = value[curPos : curPos + windowSize]
        if not curString:
            break

        lines.append("\n|    %s" % curString)
        curPos += windowSize
    return "".join(lines)


def get_obj_info(objects):
    inf = {}
    for obj in objects:
        inf.update({k: v for k, v in vars(obj).items() if k.isupper()})
    out = []
    for name, obj in sorted([(k, v) for k, v in inf.items() if k.isupper()]):
        out.append(obj_attr(obj, objName=name))
    return "\n".join(out)
