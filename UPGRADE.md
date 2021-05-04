2020-05-04: Database schema change:
```
docker exec -it aussiebbmgt /bin/bash
sqlite3 /data/aussiebbmgt.db
ALTER TABLE dpuportstatusresults ADD COLUMN status varchar(10);
```
