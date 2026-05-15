# Kas perearstiabi võimekus peab sammu rahvastiku vananemisega Eestis? — Marta Bogatõr, Mark Robin Kalder, Heti Pisarev, Inge Ringmets

## Äriküsimus

Eesmärk on uurida kuidas rahvastiku vananemine mõjutab perearstiabi koormust ja kättesaadavust Eesti maakondades. Analüüsist saavad kasu tervishoiu planeerijad, kohalikud omavalitsused ja otsustajad, kes peavad tuvastama piirkonnad, kus perearstiabile avalduv surve kasvab kõige kiiremini ning kus võib olla vaja lisarahastust, personali või teenuste ümberkorraldamist.

**Mõõdikud:**

1. 65+ elanike osakaal maakonnas
2. Perearstide arv 100 000 elaniku kohta
3. Visiidid ühe perearsti kohta

## Arhitektuur

```mermaid
flowchart LR
    source[Statistikaamet ja TAI PXWeb API] --> ingest[Python]
    ingest --> staging[(PostgreSQL)]
    staging --> transform[dbt transformatsioon]
    transform --> mart[(PostgreSQL)]
    mart --> dashboard[Power bi/Superset]
    mart --> quality[dbt andmekvaliteedi testid]
    scheduler[Airflow Scheduler] --> ingest
```

Täpsem kirjeldus: [`Docs/Arhitektuur.md`](docs/arhitektuur.md)


## Andmestik

| Allikas | Tüüp | Ajas muutuv? | Roll |
|---------|------|--------------|------|
| Statistikaamet RV022U | PXWeb API | Uueneb regulaarselt, aga harva (kord poole aasta või aasta jooksul) | Rahvastiku vanusstruktuuri analüüsimiseks. |
| TAI THT009 | PXWeb API | Uueneb regulaarselt, aga harva (kord poole aasta või aasta jooksul) | Perearstiabi võimekuse hindamiseks. |
| TAI AV40 | PXWeb API | Uueneb regulaarselt, aga harva (kord poole aasta või aasta jooksul) | Perearstiabi tegeliku koormuse mõõtmiseks |

Kui jõuame, siis lisaks:
| Allikas | Tüüp | Ajas muutuv? | Roll |
|---------|------|--------------|------|
| Statistikaamet RV084 | PXWeb API | Jah, aga prognoosiandmed uuenevad harva | Lisaanalüüs rahvastiku vananemise tulevikuprognoosi jaoks |

## Stack

| Komponent | Tööriist |
|-----------|---------|
| Sissevõtt | [Python] |
| Transformatsioon | [SQL / dbt] |
| Andmehoidla | PostgreSQL |
| Näidikulaud | [Superset / Power bi] |
| Orkestreerimine | [Airflow] |




# Ei ole tehtud:

## Käivitamine

```bash
# 1. Klooni repo ja liigu kausta
git clone <repo-url>
cd <projekti-kaust>

# 2. Kopeeri keskkonnamuutujad
cp .env.example .env
# Muuda .env failis paroolid ja muud seaded vastavalt vajadusele

# 3. Käivita teenused
docker compose up -d --build

# 4. [Vabatahtlik: käivita sissevõtt käsitsi esimesel korral]
# docker compose exec pipeline python scripts/run_pipeline.py run-all
```

Airflow (kui kasutatakse): http://localhost:8080 (kasutaja: airflow / parool: airflow)
Näidikulaud: http://localhost:[PORT]

## Saladused ja konfiguratsioon

Kõik saladused (paroolid, API võtmed, andmebaasi URL-id) on `.env` failis. Repos on ainult `.env.example`, mis näitab vajalike muutujate struktuuri ilma tegelike väärtusteta. Päris `.env` faili ei tohi GitHubi panna - see on `.gitignore`-s.

Vajalikud muutujad:

| Muutuja | Tähendus | Näide |
|---------|----------|-------|
| `DB_PASSWORD` | PostgreSQL parool | (saladus) |
| `[teised]` | ... | ... |

## Andmevoog lühidalt

1. **Sissevõtt** — [Kirjelda, kuidas andmed allikast kätte saadakse]
2. **Laadimine** — Andmed laaditakse `staging` kihti
3. **Transformatsioon** — [Kirjelda peamised arvutused ja mudelid]
4. **Testimine** — [Mitu] andmekvaliteedi testi kontrollivad korrektsust
5. **Näidikulaud** — [Kirjelda lühidalt, mida näidikulaud näitab]

## Andmekvaliteedi testid

Projekt kontrollib järgmist:

1. [Test 1 - nt: kasutajate ID on unikaalne]
2. [Test 2 - nt: tellimuse summa pole null]
3. [Test 3 - nt: kuupäev jääb vahemikku 2020-2026]
[Lisa rohkem, kui sul on]

Testide tulemused: [kuhu salvestatakse / kuidas vaadata]

## Projekti struktuur

```
.
├── README.md
├── compose.yml
├── .env.example
├── .gitignore
├── docs/
│   ├── arhitektuur.md      ← nädal 1 väljund
│   └── progress.md         ← nädal 2 väljund
└── ...                     ← ülejäänud projektifailid
```

## Kokkuvõte, puudused ja võimalikud edasiarendused

**Kokkuvõte:**
- [Loetle, mis on lõpule viidud, mis töötab hästi]

**Puudused:**
- [Loetle ausalt, mis jäi tegemata - see ei mõjuta hinnet negatiivselt, vaid aitab hinnata]

**Mis edasi:**
- [Mida tahaksid edasi teha, kui aega oleks rohkem]

## Meeskond

| Nimi | Roll |
|------|------|
| [Marta Bogatõr] | [Roll] |
| [Nimi 2] | [Roll] |
| [Nimi 3] | [Roll] |
| [Nimi 4] | [Roll — vabatahtlik] |
