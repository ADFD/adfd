import codecs
import logging
import os
import re
from datetime import datetime
from types import FunctionType, MethodType

import pytest
from plumbum import LocalPath

from adfd.bbcode import AdfdParser
from adfd.conf import DATE_FORMAT

log = logging.getLogger(__name__)


def get_paths(containerPath, ext=None, content=None):
    paths = sorted([p for p in containerPath.list()])
    if ext:
        paths = [p for p in paths if p.endswith(ext)]
    if content:
        paths = [p for p in paths if content in p]
    return paths


def date_from_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(DATE_FORMAT)


class _Slugification(object):
    """Turn sentences into slugs to be used in filenames and URLs"""
    SEP = '-'

    def __init__(self):
        # noinspection PyUnresolvedReferences
        import translitcodec  # register new codec for slugification

        self.splitter = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

    def __call__(self, text):
        words = []
        for word in self.splitter.split(text.lower()):
            word = codecs.encode(word, 'translit/long')
            if word:
                words.append(word)
        return self.SEP.join(words)

slugify = _Slugification()


class ContentGrabber(object):
    def __init__(self, absPath=None, relPath='.'):
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


def dump_contents(path, contents):
    log.debug('%s', path)
    path.dirname.mkdir()
    path.write(contents, encoding='utf8')


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


_specialAttrNames = [
    "str", "repr", "dict", "doc", "class", "delattr", "format",
    "getattribute", "hash", "init", "module", "new", "reduce", "reduce_ex",
    "setattr", "sizeof", "subclasshook", "weakref"]


SIMPLE_OBJECTS = [str, list, tuple, dict, set, int, float]


def obj_attr(obj, hideString='', filterMethods=True, filterPrivate=True,
             sanitize=False, excludeAttrs=None, indent=0, objName=""):
    try:
        if any(isinstance(obj, t) for t in SIMPLE_OBJECTS):
            return ("[%s] %s = %s" %
                    (type(obj).__name__, objName or "(anon)", str(obj)))

        return _obj_attr(
            obj, hideString, filterMethods, filterPrivate,
            sanitize, excludeAttrs, indent, objName)

    except:
        msg = "problems calling obj_attr"
        log.error(msg, exc_info=True)
        return msg


def _obj_attr(obj, hideString='', filterMethods=True, filterPrivate=True,
              sanitize=False, excludeAttrs=None, indent=0, objName="",
              terminalSize=120):
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
    numDashes = (terminalSize // 2) - len(header) // 2
    maxNameLen = max([len(name) for name in names])
    out = (
        ["\n," + "-" * (numDashes - 1) + header + "-" * numDashes] +
        [_prep_line(content, maxNameLen, maxTypeLen, terminalSize)
         for content in out] + ["'" + "-" * terminalSize])
    if sanitize:
        out = [o.replace('<', '(').replace('>', ')') for o in out]
    if indent:
        out = ["%s%s" % (" " * indent, o) for o in out]
    return os.linesep.join(out)


def _prep_line(contentTuple, maxNameLen, maxTypeLen, terminalSize):
    """add line breaks within an attribute line"""
    name, typeName, value = contentTuple
    typeName = typeName.rpartition(".")[-1]
    formattedName = name + ' ' * (maxNameLen - len(name))
    formattedType = typeName + ' ' * (maxTypeLen - len(typeName))
    pattern = "| [%s] %s %%s" % (formattedType, formattedName)
    if not isinstance(value, str):
        value = str(value)

    if value.strip().startswith("| "):
        return pattern % (value)

    windowSize = terminalSize
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


def get_config_info():
    from adfd import conf, cst

    inf = {k: v for k, v in vars(conf).items() if k.isupper()}
    inf.update({k: v for k, v in vars(cst).items() if k.isupper()})
    out = []
    for name, obj in sorted([(k, v) for k, v in inf.items() if k.isupper()]):
        out.append(obj_attr(obj, objName=name))
    return '\n'.join(out)


# todo remove, when it's blatantly obvious that I don't need it
# class Git(object):
#     def __init__(self, path):
#         self.path = path
#
#     def _git_add_files(self):
#         cmd = ['git', 'add', '--all', '.']
#         try:
#             subprocess.check_output(cmd, cwd=str(self.path))
#         except subprocess.CalledProcessError:
#             pass
#
#     def _git_prune_orphans(self):
#         for p in self.TOPICS_PATH.walk():
#             if not p.isdir() and not any(ap == p for ap in self.allPaths):
#                 log.warning("removing %s", p)
#                 cmd = ['git', 'rm', '-f', str(p)]
#                 try:
#                     subprocess.check_output(cmd, cwd=str(self.TOPICS_PATH))
#                 except subprocess.CalledProcessError:
#                     p.delete()
