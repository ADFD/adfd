class CatDesc:
    """Describe a Website category and it's contents"""
    def __init__(self, name, mainTopicId, contents):
        self.name = name
        self.mainTopicId = mainTopicId
        self.contents = contents


überUns = CatDesc('Über uns', 10694, [11220, 11223, 11222])
_ppMyth = CatDesc('Psychopharmaka Mythen', 10694, [10055, 9799, 11133])
_risiko = CatDesc('Risiken und Nebenwirkungen', 11225, [8676])
psychopharmaka = CatDesc(
    'Psychopharmaka', 11224, [9736, _ppMyth, 8507, _risiko, 10387, 10920])
_ppAb = CatDesc('Abhängig von Psychopharmaka?', 10694, [8621, 8829, 9724])
_abAllg = CatDesc('Allgemeine Tips und Hinweise', 10694, [9913, 7936, 8897])
_abAds = CatDesc('Antidepressiva absetzen', 10694, [853, 9724])
_abBen = CatDesc('Benzodiazepine absetzen', 10694, [2207, 3462, 4694])
_ABnL = CatDesc('Neuroleptika absetzen', 10694, [8022, 11137])
_AbWeit = CatDesc('Weitere Absetzinformationen', 10694, [10199])
absetzen = CatDesc('Absetzen', 10694, [_ppAb, _abAllg, _abAds, _abBen, _ABnL])
_entUm = CatDesc(
    'Umgang mit Entzugssymptomen', 10694,
    [11218, 9345, 6442, 7663, 9910, 9778])
_entBeg = CatDesc(
    'Umgang mit Begleit- und Folgeerkrankungen', 10694, [10848])
_entHil = CatDesc('Psychosoziale Hilfen', 10694, [10007])
entzug = CatDesc('Hilfe beim Entzug', 10694, [_entUm, _entBeg, _entHil])
alternativen = CatDesc('Alternativen', 10694, [7721, 9941, 10940])
medien = CatDesc('Medienberichte und Publikationen', 10694, [10932, 10870])
dev = CatDesc('[DEV]', 10694, [10068, 11217])


SITE_DESCRIPTION = CatDesc(
    '', 11221,
    [überUns, psychopharmaka, absetzen, entzug, alternativen, medien, dev])
