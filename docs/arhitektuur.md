# Arhitektuur

## Äriküsimus

**!NB! Kuna Algselt planeeritud andmed olid liiga staatilised, siis muutsime teemat**

Uus eesmärk on uurida kuidas iganädalane ilm (temperatuur, sademed ja tuul) on seotud surmajuhtude ja liiklusõnnetuste arvuga. Näiteks kas väga kuumade või väga külmade ilmadega on rohkem surmajuhte ja/või liiklusõnnetusi. Liiklusõnnetuste analüüsis on võimalik eristada ka maakonda.

## Mõõdikud -- _tuleb veel lahti kirjutada valemite tasemel_

1. Surmajuhtude arv nädalas vanuse lõikes
2. Nädala keskmine temperatuur, päikesepaiste hulk
3. Liiklusõnnetuste arv, vigastatute ja hukkunute arv ööpäevas maakondade lõikes
4. Ööpäeva keskmine temperatuur, sademete hulk maakondade lõikes
 
## Andmeallikad

| Allikas | Tüüp | Uuenemise sagedus | Roll | Link |
|---------|------|--------------|------|------|
| Statistikaamet RV035 | json | kord nädalas | Sisaldab **surmade arve** aasta, nädala, vanuserühma (0-64, 65-79, 80+) ja soo järgi. | link[https://andmed.stat.ee/et/stat/rahvastik__rahvastikusundmused__surmad/RV035/table/tableViewLayout2] |
| Keskkonnaportaal | json | kord tunnis | Sisaldab **ilmamõõtmisi** eestis tunni ja jaama kaupa | https://keskkonnaportaal.ee/et/avaandmed/keskkonna-ja-ilma-valdkonna-andmeteenused |
| Transpordiamet | csv | kord nädalas | sisaldab **liiklusõnnetusi**, osalejate arv, vigatsatud ja hukkunud inimesi, maakond | https://andmed.eesti.ee/datasets/inimkannatanutega-liiklusonnetuste-andmed |


## Andmevoog

```mermaid
flowchart LR
source[Statistikaamet]  --> ingest[Python]
source2[Keskkonnaagentuur] --> ingest[Python]
source3[Transpordiamet] --> ingest[Python]
    ingest --> staging[(PostgreSQL)]
    staging --> transform[dbt transformatsioon]
    transform --> mart[(PostgreSQL)]
    mart --> dashboard[Power bi/Superset]
    mart --> quality[dbt andmekvaliteedi testid]
    scheduler[Cron] --> ingest
```

## Andmebaasi kihid

| Kiht | Roll |
|------|------|
| `Bronze staging` | Hoiab allikatest saadud andmeid võimalikult töötlemata kujul. Siia jõuavad PXWeb API vastustest laetud rahvastiku, ilma ja liiklusõnnetuste andmed. |
| `Silver intermediate` | Puhastab ja ühtlustab andmed, et erinevad allikad läheksid kokku ajaraamis (nädala või kuu kaupa), maakondade nimed, aastad, vanuserühmad jne viiakse samale kujule. |
| `Gold mart` | Hoiab transformeeritud ja äriloogikat sisaldavaid tabeleid, mida kasutatakse pärast dashboard'is. Siin arvutatakse näiteks: surmajuhtude arv, ööpäeva keskmine temperatuur, sademed ja tuulekiirus, 65+ elanike osakaal ja liiklusõnnetuste arv ühtses ajaperioodis. |


## Tööjaotus

| Roll | Vastutus | Täitja |
|------|----------|--------|
| Andmeallika omanik | Kirjutab sissevõtu loogika, hoiab API-t töös | Inge, Heti |
| Transformatsioonide omanik | Kirjutab mart kihi mudelid ja mõõdikute arvutuse | Mark |
| Kvaliteedi omanik | Kirjutab testid ja vaatab läbi ebaõnnestunud kontrollid | Inge, Heti |
| Näidikulaua omanik | Ehitab näidikulaua ja seob selle äriküsimusega | Marta |

## Riskid

| Risk | Mõju | Maandus |
|------|------|---------|
| API struktuur või tabeli kood muutub | Python sissevõtu skript võib ebaõnnestuda või laadida valed andmed | Hoida allikate URL-id ja päringuparameetrid eraldi konfiguratsioonis ning lisada kontroll, kas oodatud veerud on olemas |
| Maakondade nimed või koodid ei ühti eri allikates | Andmeid ei saa korrektselt ühendada maakonna tasemel | Luua dimension table, kus maakondade nimed ja koodid standardiseeritakse |


## Privaatsus ja turve

Projekt kasutab avalikke koondandmeid Statistikaametist ja Keskkonnaagentuuirst ja Transpordiamet (_võibolla_). Andmed on esitatud maakonna ja aasta tasemel ning ei sisalda üksikisikute nimesid, isikukoode, aadresse ega muid otseseid isikuandmeid, seega ei ole projektis vaja isikuandmeid anonümiseerida. 
