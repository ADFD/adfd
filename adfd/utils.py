import logging
import os
from types import FunctionType, MethodType

import pytest
from plumbum import LocalPath

from adfd import cst
from adfd.bbcode import AdfdParser


log = logging.getLogger(__name__)


class ContentGrabber(object):
    def __init__(self, relPath='.', absPath=None):
        if absPath:
            self.rootPath = absPath
        else:
            self.rootPath = LocalPath(__file__).up(2) / relPath

    def get_lines(self, fName):
        """get lines as list from file (without empty element at end)"""
        return self.strip_whitespace(self.get_text(fName))

    def get_text(self, fName, ext='.bb'):
        return self.grab(self.rootPath / (fName + ext))

    def grab(self, path=None):
        path = path or self.rootPath
        return path.read('utf-8')

    def strip_whitespace(self, content):
        """lines stripped of surrounding whitespace and last empty line"""
        lines = [t.strip() for t in content.split('\n')]
        if not lines[-1]:
            lines.pop()
        return lines


class ContentDumper(object):
    def __init__(self, path, content):
        self.path = path
        self.content = content

    def dump(self):
        self.path.write(self.content, encoding='utf-8')


class DataGrabber(ContentGrabber):
    DATA_PATH = LocalPath(__file__).up() / 'tests' / 'data'

    def __init__(self, relPath='.', absPath=None):
        super(DataGrabber, self).__init__(relPath, absPath)
        if not absPath:
            self.rootPath = self.DATA_PATH / relPath

    def get_chunks(self, fName):
        """separates chunks separated by empty lines

        :returns: list of list of str
        """
        chunks = []
        currentChunkLines = []
        for line in self.get_lines(fName):
            if line:
                currentChunkLines.append(line)
            else:
                chunks.append(currentChunkLines)
                currentChunkLines = []
        return chunks

    def get_boolean_tests(self, fName, good='good'):
        return [(l, good in l) for l in self.get_lines(fName)]

    def get_pairs(self):
        paths = [p for p in sorted(self.rootPath.list())]
        idx = 0
        contents = []
        while idx + 1 < len(paths):
            fName = paths[idx].basename
            src = self.grab(paths[idx])
            exp = self.grab(paths[idx + 1])
            contents.append((fName, src, exp))
            idx += 2
        return contents


class PairTester(object):
    _parser = AdfdParser()

    @classmethod
    def test_pairs(cls, fName, src, exp):
        exp = exp.strip()
        if not exp:
            pytest.xfail(reason='no expectation for %s' % (fName))
        print(fName)
        html = cls._parser.to_html(src)
        print("\n## RESULT ##")
        print(html)
        print("\n## EXPECTED ##")
        print(exp)
        refPath = DataGrabber.DATA_PATH / ('%s.html' % (fName))
        try:
            assert html == exp
            refPath.delete()
        except AssertionError:
            with open(str(refPath), 'w') as f:
                f.write(html)
            raise


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
