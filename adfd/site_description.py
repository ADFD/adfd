"""
[b]Über uns[/b](ADFD - Geschichte, Aufbau, Ziele)
   - Geschichte
   - Ziele
   - Lexikon

[b]Psychopharmaka[/b](Risiken und Nebenwirkungen)

    - 10 Mythen über Psychopharmaka (Götzsche) http://www.adfd.org/austausch/viewtopic.php?f=6&t=10055
           *Mythos Serotonin (Text von Dr. Healy)

    - 13 Gründe Psychopharmaka-kritisch zu sein http://www.adfd.org/austausch/viewtopic.php?f=6&t=8507

    - Abhängig von Psychopharmaka? (u.a. Diskussion des Abhängigkeitsbegriffs)
           *Antidepressiva-Einnahme und Entzug http://www.adfd.org/austausch/viewtopic.php?f=6&t=8621
           *Rezeptorenbelegung http://www.adfd.org/austausch/viewtopic.php?f=19&t=8829
           *Johanna Moncrieff: Der Mythos der chemischen Heilung http://adfd.org/austausch/viewtopic.php?f=6&t=11133

    - Antidepressiva und Schwangerschaft http://www.adfd.org/austausch/viewtopic.php?f=6&t=8676
    - Differenzialdiagnose der Depression http://www.adfd.org/austausch/viewtopic.php?f=6&t=9736
    - Antidepressiva-Absetzsyndrom http://www.adfd.org/austausch/viewtopic.php?f=6&t=9724
    - Das Serotonin-Syndrom
    - Gebrauchs- vs Fachinformation
    - Johanniskraut

[b]Absetzen[/b]

   - Allgemeine Tipps und Hinweise
         *FAQ Absetzen http://www.adfd.org/austausch/viewtopic.php?f=19&t=9913
          *Wasserlösemethode http://www.adfd.org/austausch/viewtopic.php?f=16&t=7936
           *Kügelchenmethode http://www.adfd.org/austausch/viewtopic.php?f=19&t=8897

   - Antidepressiva Absetzen
          * Infopaket http://www.adfd.org/austausch/viewtopic.php?f=19&t=853
          * SSRI-Absetzsyndrom http://www.adfd.org/austausch/viewtopic.php?f=6&t=9724

   - Benzodiazepine absetzen
           *Allgemeine Infos und Umrechnungstabellen http://www.adfd.org/austausch/viewtopic.php?f=19&t=2207
          *FAQ Benzos http://www.adfd.org/austausch/viewtopic.php?f=16&t=3462
          *Ashton Manual
          *Wasserflaschenmethode http://www.adfd.org/austausch/viewtopic.php?f=16&t=4694
          *Z-drugs

   - Neuroleptika absetzen
          *Entzugssymptome bei Neuroleptika http://www.adfd.org/austausch/viewtopic.php?f=19&t=8022
          *Niederpotente Neuroleptika (Peter Lehmann) http://www.adfd.org/austausch/viewtopic.php?f=32&t=11137

   - Medikamentensteckbriefe

   - Weitere Absetzinformationen (u Leitschriften) http://www.adfd.org/austausch/viewtopic.php?f=19&t=10199

[b]Hilfe beim Entzug [/b]

   - Umgang mit Entzugssymptomen
          *Checkliste Entzugssymptome http://www.antidepressiva-absetzen.de/Stufe_3.html
          * Entzug oder Grunderkrankung? http://www.adfd.org/austausch/viewtopic.php?f=19&t=9345
          *Symptomtrigger http://www.adfd.org/austausch/viewtopic.php?f=19&t=6442
          * Was tun gegen Entzugssymptome http://www.adfd.org/austausch/viewtopic.php?f=15&t=7663
          *Gereiztes ZNS/Funktionsstörung http://www.adfd.org/austausch/viewtopic.php?f=19&t=9910
          *Neuroemotionen beim Absetzen http://www.adfd.org/austausch/viewtopic.php?f=50&t=9778

   - Umgang mit Begleit- und Folgeerkrankungen
          *PPI
         *HIT
          *Vitaminmangel
         *Magendarmprobleme/Übelkeit
         *PMS/Zyklus/Hormonstörungen
         *Kopfschmerzen
         *Hashimoto und Absetzen http://www.adfd.org/austausch/viewtopic.php?f=57&t=10848
         *Antibiotikaeinnahme im Entzug

   - Wie können Ärzte und Angehörige helfen

   - Psychosoziale Hilfen
         *Kritische und unabhängige Institutionen/Vereinigungen http://www.adfd.org/austausch/viewtopic.php?f=15&t=10007
         *Ambulante Psychiatrische Hilfen
          *Psychotherapie

   - andere hilfreiche Websites und Organisationen

[b]Alternativen[/b]
   - Schlafhygiene
  - Mentale Techniken http://www.adfd.org/austausch/viewtopic.php?f=4&t=7721
  - 50 Hausmittel gegen Depression und Angst http://www.adfd.org/austausch/viewtopic.php?f=4&t=9941
   - Umgang mit dysfunktionalem Verhalten, Rückfällen und Schmerz
   -  Pflanzliche Alternativen
   - Notfallkoffer für die Krise http://www.adfd.org/austausch/viewtopic.php?f=50&t=10940
   - Psychosoziale Hilfen (siehe Hilfe beim Entzug)

[b]Erfahrungsberichte[/b]

[b]Medienberichte und Publikationen[/b]
  - Artikel
  - Dokumentationen
  - Literaturtipps
  - wiss. Publikationen

------------------------------------------------------------------------------

[u]
Legende:[/u]

[b]Hauptkategorie[/b](Beschreibung der Kategorie)
- Unterkategorie 1. Ordnung(Beschreibung der Kategorie)
* Unterkategorie 2. Ordnung(Beschreibung der Kategorie)
"""
from adfd.structure import CatDesc

überUns = CatDesc('Über uns', 10694, [])

_ppAb = CatDesc(
    'Abhängig von Psychopharmaka?', 10694, [8621, 8829, 11133])
psychopharmaka = CatDesc(
    'Psychopharmaka', 10694, (10055, 8507, _ppAb, 8676, 9736, 9724))


_abAllg = CatDesc(
    'Allgemeine Tips und Hinweise', 10694, [9913, 7936, 8897])
_abAds = CatDesc('Antidepressiva absetzen', 10694, [853, 9724])
_abBen = CatDesc('Benzodiazepine absetzen', 10694, [2207, 3462, 4694])
_ABnL = CatDesc('Neuroleptika absetzen', 10694, [8022, 11137])
_AbWeit = CatDesc('Weitere Absetzinformationen', 10694, [10199])
absetzen = CatDesc('Absetzen', 10694, [_abAllg, _abAds, _abBen, _ABnL])

_entHil = CatDesc('Psychosoziale Hilfen', 10694, [10007])
_entUm = CatDesc(
    'Umgang mit Entzugssymptomen', 10694, [9345, 6442, 7663, 9910, 9778])
_entBeg = CatDesc(
    'Umgang mit Begleit- und Folgeerkrankungen', 10694, [10848])
entzug = CatDesc('Hilfe beim Entzug', 10694, [_entUm, _entBeg, _entHil])


alternativen = CatDesc('Alternativen', 10694, [7721, 9941, 10940])
dev = CatDesc('[DEV]', 10694, [10068, 11217])


SITE_DESCRIPTION = CatDesc(
    '', 10694, [überUns, psychopharmaka, absetzen, entzug, dev])
