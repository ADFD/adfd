"""
Create statistics about developments in ADFD.

Some ideas:

* development of posts per day/month/year
* development of new users per day/month/year
* development of new topics per day/month/year
* development of ratio of moderator/admin posts to posts of normal users
* development of mentions of sepcific substances (synonyms/fuzzy/star notation)
* Find some module that downloads all awstats to analyze access
* sum of all thanks
"""
import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from adfd.db.lib import get_db_session


log = logging.getLogger(__name__)


class DataFetcher:
    def __init__(
            self, tableName='phpbb_posts',
            timeColumn='post_time', timeFmt='%Y/%m/%d',
            columnNames=('post_id', 'topic_id', 'poster_id', 'forum_id',)):
        self.session = get_db_session()
        self.table = tableName
        self.timeColumn = timeColumn
        self.timeFmt = timeFmt
        self.fmt = "from_unixtime(%s, '%s')" % (self.timeColumn, self.timeFmt)
        self.columnNames = columnNames
        self.where = None
        self.data = []

    def get_series(self):
        indizes = []
        data = []
        for row in self.fech_raw_data():
            indizes.append(row[0])
            data.append(row[1:])
        datetimeIndex = np.array(indizes).astype('datetime64[s]')
        return pd.Series(index=datetimeIndex, data=1)

    def get_compacted(self):
        for row in self.fech_raw_data():
            dataDict = {a: b for a, b in zip(self.columnNames, row[2:])}
            self.data.append((row[0], row[1], dataDict))
        return self.data

    def fech_raw_data(self):
        return self.session.execute(self.statement)

    @property
    def statement(self):
        statement = self.select
        if self.where:
            statement += " %s" % self.where
        return statement

    @property
    def select(self):
        return ("SELECT %s, %s, %s FROM %s" %
                (self.timeColumn, self.fmt, self.columList, self.table))

    def set_time_range(self, start='2003/10/09', end='2003/10/10'):
        self.where = (
            "WHERE (%s) BETWEEN '%s' AND '%s'" % (self.fmt, start, end))

    @property
    def columList(self):
        return ", ".join(self.columnNames)


class StatsPlotter:
    def __init__(self, series, xlabel=u"Zeit", ylabel=u"Beiträge"):
        # self.series = series
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.series = series.resample('M').sum()
        plt.figure()
        self.plt_format()

    def plt_format(self):
        # plt.style.use('fivethirtyeight')
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        # plt.legend(loc='best')
        plt.tight_layout()

        # fmt = dates.DateFormatter('%Y')
        # loc = dates.MonthLocator(by=[1, 4, 7, 10])
        # ax = plt.axes()
        # ax.xaxis.set_major_formatter(fmt)
        # ax.xaxis.set_major_locator(loc)
        # plt.locator_params(axis='x', nbins=10)
        # plt.locator_params(axis='y', nbins=20)

    def show(self):
        self.series.plot()
        plt.show()

    def save(self, name):
        self.series.plot()
        F = plt.gcf()
        dpi = F.get_dpi()
        inches = F.get_size_inches()
        print(dpi * inches)
        plt.savefig('%s.png' % name)


def series_stats():
    df = DataFetcher()
    df.set_time_range(start='2005/01/01', end='2018/02/28')
    sp = StatsPlotter(df.get_series())
    sp.save('teststats')
    print("saved to teststats.png")
    # print(obj_attr(sp.series))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    series_stats()
