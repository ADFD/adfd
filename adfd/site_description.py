from adfd.structure import CatDesc

absetzen = CatDesc('Absetzen', 10694, [9913, 9910, 853])
steckbriefe = CatDesc('Steckbriefe', 10694, [9738, 9735, 9733, 9732, 9731])
geschichte = CatDesc('Geschichte', 10694, [9913, 9910, 853])
hintergründe = CatDesc('Hintergründe', 10694, (steckbriefe, geschichte))
info = CatDesc('Info', 10694, [689, 893])
bbcode = CatDesc('BBcode', 10694, [10068])

SITE_DESCRIPTION = CatDesc('', 10694, (absetzen, hintergründe, info, bbcode))
