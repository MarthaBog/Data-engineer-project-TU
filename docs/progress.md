# Edenemisraport

## Mis on valmis

- [X] Docker Compose käivitab kõik teenused
- [X] Andmeid saadakse allikast kätte
- [X] Andmed laetakse `staging` kihti
- [X] Vähemalt üks transformatsioon toimib
- [X] Vähemalt üks näidikulaud on nähtaval
- [X] Vähemalt üks andmekvaliteedi test läbib

Ülekanne ja transformeerimine on valmis, kogu projekti töövoog on läbi tehtud, aga projekt ei käivitu veel automaatselt.

- Superset dashboard:
    - On valmis: Superseti visualiseerimiskeskkond ja esimene interaktiivne näidikulaud. 
       - Superset lisati Docker Compose faili eraldi teenusena ja ühendati PostgreSQL andmebaasiga 'ilm_surm_liiklus'. Kuna Superseti Docker image'is puudus PostgreSQL ühenduse jaoks vajalik draiver, loodi eraldi superset.Dockerfile, kuhu lisati 'psycopg2-binary'(ühendab baas ja Supeset).
       - Superseti jaoks loodi eraldi metadata-andmebaas superset, kus hoitakse Superseti sisemisi objekte, näiteks kasutajaid, andmebaasiühendusi, datasette, graafikuid ja näidikulaudu.
    - Supersetis kasutatakse kaks mart-tabelit:
        - 'public.mart_deaths_weather_weekly_nationa'`
        - 'public.mart_traffic_weather_weekly_county'
    - Lisaks loodi SQL Labis virtuaalne dataset, kus surmajuhtumid, liiklusõnnetused ja ilmastikunäitajad ühendati nädalapõhiseks analüüsiks. Selle põhjal koostati standardiseeritud nädalaste kõrvalekallete graafik.
    - Näidikulauale lisati interaktiivsed filtrid. 
        Filtrid ei mõjuta kõiki graafikuid ühtemoodi, sest visuaalid põhinevad erinevatel mart-tabelitel.

Näidikulaual on loodud:
- KPI-kaardid:
'Surmajuhtumid kokku', 'Liiklusõnnetused kokku', 'Hukkunud liikluses kokku', 'Keskmine temperatuur (°C)'.
- Graafikud:
    - 'Surmajuhtumid vanuserühmiti' 
    - 'Liiklusõnnetused maakonniti' 
    - 'Keskmine surmajuhtumite ja õnnetuste arv temperatuurikategooria järgi' -  Võrdleb keskmist surmajuhtumite ja liiklusõnnetuste arvu erinevates temperatuurikategooriates.
    - 'Nädalased kõrvalekalded: ilm, surmad ja liiklusõnnetused'  
    Näitab standardiseeritud nädalasi kõrvalekaldeid, et erineva skaalaga näitajaid oleks võimalik võrrelda ühel graafikul.

Standardiseerimise jaoks kasutati z-score põhimõtet:

```
z = (x - keskmine väärtus) / standardhälve
```

## Järgmised sammud

- Ajastamine
- Näidikulaua sisu ülevaatamine
- Andmekvaliteedi test

## Mis takistab

- Ingel ja Hetil ei õnnestu Superseti dashboardi käima saada
- Näidikulaual standardiseeritud temperatuur käitub tagurpidi

## Kontrollpunkt

<!-- Käsk, millega saab kontrollida, et töövoog töötab:

```bash
docker compose exec pipeline python scripts/run_pipeline.py check
``` -->

Käsk, millega saab kontrollida, et töövoog töötab:
```bash
docker compose up -d --build
docker compose ps
```
Lisaks saab kontrollida, et PostgreSQL andmebaas on kättesaadav:
```bash
docker compose exec db psql -U projekt -d ilm_surm_liiklus -c "\dt public.*"
```
Superseti konteineri kontrollimiseks:
```bash
docker compose exec superset python -c "import psycopg2; print('psycopg2 ok')"
```


**Superseti avamiseks** (igas arvutis eraldi, cloud ei ole):
```bash
docker compose up -d --build
docker compose --profile dbt run --rm dbt seed
docker compose --profile dbt run --rm dbt run
```

Superset link (parool failis ".env")
http://localhost:8088

Supersetis avada:
**Settings → Database Connections → Ilm Surm Liiklus PostgreSQL → Edit**

Sisesta SQLAlchemy URI:
**postgresql://projekt:pass@db:5432/ilm_surm_liiklus**

Import dashboard:
Dashboards → Import → lisada zip-file kaustast "superset_exports"


