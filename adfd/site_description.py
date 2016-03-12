from adfd.structure import CatDesc

absetzen = CatDesc('Absetzen', 10694, [9913, 9910, 853])
steckbriefe = CatDesc('Steckbriefe', 10694, [9738, 9735, 9733, 9732, 9731])
geschichte = CatDesc('Geschichte', 10694, [9913, 9910, 853])
hintergründe = CatDesc('Hintergründe', 10694, (steckbriefe, geschichte))
info = CatDesc('Info', 10694, [689, 893])
linaSammlung = CatDesc(
    'Linas Liste', 11211,
    [10199, 2207, 853, 9913, 3462, 7936, 8897, 4694, 8022, 6442, 7663,
     9910, 9778, 8829, 8621, 9345, 10055, 8507, 11133, 9736, 1896, 3462,
     11137, 9724, 7819, 9278])
bbcode = CatDesc('BBcode', 10694, [10068])

SITE_DESCRIPTION = CatDesc(
    '', 10694, (absetzen, hintergründe, info, linaSammlung, bbcode))
