import logging
import os

from adfd.process import date_from_timestamp
from plumbum import LocalPath

log = logging.getLogger(__name__)


class ContentGrabber:
    def __init__(self, path):
        self.path = LocalPath(path)

    def get_lines(self, fName=None):
        """get lines as list from file (without empty element at end)"""
        path = self.path / (fName + '.bb') if fName else self.path
        return self.strip_whitespace(self.grab(path))

    def grab(self, path=None):
        path = path or self.path
        return path.read('utf-8')

    def get_ctime(self):
        return date_from_timestamp(os.path.getctime(self.path))

    def get_mtime(self):
        return date_from_timestamp(os.path.getmtime(self.path))

    @staticmethod
    def strip_whitespace(content):
        """lines stripped of surrounding whitespace and last empty line"""
        lines = [t.strip() for t in content.split('\n')]
        if not lines[-1]:
            lines.pop()
        return lines
