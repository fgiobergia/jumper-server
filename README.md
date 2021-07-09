## Creating a new db
Use `createdb.sql` to create a new sqlite database (e.g. `storage.db`).
Open the database with sqlite to manually add users (this is currently the only way of adding new users).

```
$ sqlite3 storage.db < createdb.sql 
$ sqlite3 storage.db 
SQLite version 3.24.0 2018-06-04 14:10:15
Enter ".help" for usage hints.
sqlite> insert into users (id) values (1234);
```