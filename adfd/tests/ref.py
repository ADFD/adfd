from adfd.adfd_parser import AdfdParser
from test_adfd_parser import get_pairs

for fName, src, exp in get_pairs():
    if 'ordered-list' not in fName:
        continue

    parser = AdfdParser()
    result = parser.format(src)
    print result
