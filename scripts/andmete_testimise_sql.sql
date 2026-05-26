 select count(*)  from onnetused ; 
 select count(*) from surmad ;  
  select count(*) from ilm ;  


 select *  from onnetused limit 5 ; 
 select * from surmad limit 5; 
 select * from ilm limit 5;



  select surmad."Näitaja", count(*) from surmad group by surmad."Näitaja";  

 select surmad."Nädal", count(*) from surmad group by surmad."Nädal";  
 select element_nimi_eng  from ilm group by element_nimi_eng ;

 select substr(kuupaev, 1, 4), count(distinct id), sum(hukkunud), sum(vigastatud)  
 from onnetused  
 group by substr(kuupaev, 1, 4);

 select maakond, count(distinct id), sum(hukkunud), sum(vigastatud)  
 from onnetused  
 where substr(kuupaev, 1, 4) = '2025'
 group by maakond;

 select "Vaatlusperiood", "Vanuserühm", sum(value) 
 from surmad 
 where "Sugu" = 'Mehed ja naised'
 and "Nädal" = 'Nädalad kokku'
 and "Näitaja" = 'Surmade arv'
 group by  "Vaatlusperiood", "Vanuserühm";

 select "Vaatlusperiood", "Vanuserühm", sum(value) 
 from surmad 
 where "Sugu" = 'Mehed ja naised'
 and "Nädal" <> 'Nädalad kokku'
 and "Näitaja" = 'Surmade arv'
 group by  "Vaatlusperiood", "Vanuserühm";

select * from surmad 
 where "Sugu" = 'Mehed ja naised'
 and "Nädal" <> 'Nädalad kokku'
 and "Näitaja" = 'Surmade arv'
 and "Vaatlusperiood" = '2026';


select aasta, count(distinct paev), count(distinct jaam_kood), count(*)
from ilm
 group by aasta;