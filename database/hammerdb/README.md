# HammerDB

## Setup database

Check mysql/postgresql readme.md to setup the subsequent databases.

## Install 

```
wget https://github.com/TPC-Council/HammerDB/releases/download/v4.8/HammerDB-4.8-Linux.tar.gz
tar -zxvf HammerDB-4.8-Linux.tar.gz 
```

## Run

1. For PostgresQL
```
./bench.sh -d <HAMMER_DB_PATH> -u postgres -p postgres -w 1 -t fill,bench -v 1 -db pg -r 1 -port 5432 -b 1 -n "-C 6-11" -dbc "0-5" -o /home/ubuntu/HammerRuns --verbose
```
2. For MySQL
```
./bench.sh -d <HAMMER_DB_PATH> -u root -p mysql -w 1 -t fill,bench -v 1 -db mysql -r 1 -port 5432 -b 1 -n "-C 6-11" -dbc "0-5" -o /home/ubuntu/HammerRuns --verbose
```