# dbt transformatsioonikiht

Projekti dbt-mudelite ülesehitus, granulaarsused ja piiranguid.

## Lühikokkuvõte

Transformatsioonikiht ehitab kolme toortabeli peale kaks lõplikku analüüsitabelit:

| Väljund | Granulaarsus | Eesmärk |
|---|---|---|
| `mart_deaths_weather_weekly_national` | üks rida `nädal x vanuserühm x sugu` kohta | seob riiklikud nädalased surmad riikliku ilma ja sama nädala varasemate aastate võrdlusega |
| `mart_traffic_weather_weekly_county` | üks rida `nädal x maakond` kohta | seob maakondlikud nädalased liiklusnäitajad maakondliku ilma ja sama nädala varasemate aastate võrdlusega |

Surmade andmestik ei sisalda maakonda, seetõttu ei ole selles töös võimalik koostada maakondlikku surmade marti praeguste andmeallikatega.

## Transformatsioonikihtide ülevaade

- `stg_*` parandab tüüpe, peidab ära allikaspetsiifilise segaduse
- `int_*` joondab allikad samale nädalapõhisele ärigranulaarsusele
- `dim_*` ja `fct_*` annavad taaskasutatava kihi
- `mart_*` on lõplikud analüüsitabelid, mida saab kasutada näidikulauas

Faktid ja dimensioonid on ehitusplokid, millest saab vajadusel ka jooksvalt päringuid koostada, `mart_*` tabelid on konkreetse äriküsimuse lõppväljundid.

## Kihid detailsemalt

### 1. Toorandmed

Pythoni skriptid laevad andmed toortabelitesse:

- `raw.surmad`
- `raw.onnetused`
- `raw.ilm`

dbt käsitleb neid `source('raw', ...)` objektidena. Selles kihis ei tehta äriloogikat dbt-s.

### 2. Staging `stg_*`

Staging kiht puhastab, muudab väljade tüüpe ja ühtlustab toorandmed järgmistele kihtidele sobivaks.

- `stg_surmad`
  - teisendab aasta ja nädala ISO kujule
  - jätab alles ainult read, kus `"Näitaja" = 'Surmade arv'`
  - eemaldab read `"Nädalad kokku"`
  - eemaldab `NaN` väärtused
  - tulemus: `nädal x sugu x vanuserühm`

- `stg_onnetused`
  - muudab kuupäeva ja kella tüübid
  - normaliseerib maakonna nime
  - arvutab ISO aasta, ISO nädala ja `week_key`
  - tulemus: üks rida ühe liiklusõnnetuse kohta

- `stg_ilm`
  - muudab jaamade, kuupäevade ja mõõdikute tüübid
  - filtreerib välja ainult projekti jaoks vajalikud ilmamõõdikud
  - arvutab ISO aasta, ISO nädala ja `week_key`
  - tulemus: `jaam x päev x mõõdik`

Staging ei ole siin “toorandmete koopia”, vaid juba puhastatud ja ühtlustatud kiht.

### 3. Intermediate `int_*`

Intermediate kiht viib eri allikad ühele analüütilisele tasemele, peamiselt nädala granulaarsusele, ning valmistab ette võrdlusnäitajad.

#### Ilma mudelid

- `int_ilm_daily_station`
  - pivotib pika formaadi ilmamõõtmised laia formaati
  - tulemus: `jaam x päev`

- `int_ilm_daily_county`
  - seob ilmajaamad maakondadega kasutades `station_county_map`
  - arvutab ühe päeva kohta maakonna keskmise üle kõigi maakonna jaamade
  - tulemus: `maakond x päev`

- `int_ilm_weekly_station`
  - koondab jaamapõhised ilmaandmed nädalaks
  - tulemus: `jaam x nädal`

- `int_ilm_weekly_county`
  - koondab maakonnapõhised päeva ilmaandmed nädalaks
  - arvutab keskmise temperatuuri, summaarse sademete hulga, summaarse päikesepaiste hulga, tuule keskmise ning äärmuslike päevade loendurid
  - tulemus: `maakond x nädal`

- `int_ilm_weekly_national`
  - arvutab riikliku nädala taseme ilmaandmed maakond x päev ridade pealt
  - tulemus: `nädal`

Riiklik ilm ei tule otse jaamadest, vaid maakond x päev agregeerimise kaudu.

#### Liikluse mudelid

- `int_onnetused_weekly_county`
  - loendab õnnetuste arvu ning summeerib vigastatute ja hukkunute arvu
  - tulemus: `maakond x nädal`

#### Ajaloolise võrdluse mudelid

- `int_surmad_weekly_hist`
  - tulemus: `nädal x vanuserühm x sugu`

- `int_onnetused_weekly_county_hist`
  - tulemus: `maakond x nädal`

- `int_ilm_weekly_county_hist`
  - tulemus: `maakond x nädal`

- `int_ilm_weekly_national_hist`
  - tulemus: `nädal`

Kõigis `*_hist` mudelites kasutatakse sama põhimõtet: sama ISO nädala varasemate aastate keskmine. See ei ole põhjuslik mudel ega standardiseeritud anomaalia, vaid lihtne ajalooline võrdlusbaas.

Kui lõppmartis on väli kujul `*_vs_hist`, siis selle tähendus on:

`käesoleva nädala väärtus - sama ISO nädala varasemate aastate keskmine`

## Marts-kiht

Marts kiht sisaldab kahtesid eri tüüpi mudeleid - taaskasutatavaid dimensiooni- ja faktitabeleid ning lõplikuid marts analüüsitabeleid.

### Dimensioonid

- `dim_week`

- `dim_county`

- `dim_age_group`

- `dim_sex`

- `dim_weather_station`

### Faktitabelid

- `fct_deaths_weekly`
  - `nädal x vanuserühm x sugu`

- `fct_traffic_weekly_county`
  - `nädal x maakond`

- `fct_weather_weekly_station`
  - `nädal x jaam`

- `fct_weather_weekly_county`
  - `nädal x maakond`

Need on vahekihid, mida saab kasutada ka muude lõppmartide ehitamiseks.

### Lõplikud analüüsimardid

#### `mart_deaths_weather_weekly_national`

Granulaarsus on üks rida `nädal x vanuserühm x sugu` kohta.

Tulpade kirjeldused:
- surmade arv
- surmade ajalooline sama nädala keskmine
- surmade kõrvalekalle ajaloolisest keskmisest
- riiklikud ilmanäitajad
- riiklike ilmade ajaloolised sama nädala keskmised
- ilmade kõrvalekalded ajaloolistest keskmistest

#### `mart_traffic_weather_weekly_county`

Granulaarsus on üks rida `nädal x maakond` kohta.

Tulpade kirjeldused:
- õnnetuste arv
- vigastatute arv
- hukkunute arv
- nende ajaloolised sama nädala keskmised
- maakondlikud ilmanäitajad
- ilmade ajaloolised sama nädala keskmised
- kõrvalekalded ajaloolistest keskmistest

## Ilma metoodika täpsustus

Maakondlik ilm:

1. `stg_ilm` valib vajalikud mõõdikud ja tüübid.
2. `int_ilm_daily_station` teeb jaamapõhise päevarea.
3. `int_ilm_daily_county` keskmistab sama maakonna jaamade päevased mõõtmised.
4. `int_ilm_weekly_county` koondab maakonnapäevad nädalaks.

Riiklik ilm:

1. aluseks on `int_ilm_daily_county`
2. `int_ilm_weekly_national` agregeerib maakondade päevased andmed riiklikuks nädalaks

## Piirangud

### Surmade andmete piirang

Surmade allikas on Statistikaameti tabel `RV035`, kus granulaarsus on nädal, sugu ja vanuserühm. Maakonna tunnust selles allikas ei ole. Seetõttu ei saa teha maakondlikku surmade marti.

### Ilmajaamade katvus

`county_seed` sisaldab kõiki 15 maakonda, kuid `station_county_map` sisaldab neist 14, kuna Põlva maakonnal puudub ilmajaam. Maakondliku ilma katvus ei ole täielik.

