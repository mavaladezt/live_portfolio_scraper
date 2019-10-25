#Create Database

touch stock.db

sqlite3 stock.db

.tables
.headers ON
.mode column

CREATE TABLE history (
        date DATE,
        high NUMERIC,
        low NUMERIC,
        open NUMERIC,
        close NUMERIC,
        volume NUMERIC,
        adjclose NUMERIC,
        symbol VARCHAR(10)
        );

Check available tables: sqlite>

#Create table
CREATE TABLE live (
        date DATE,
        open NUMERIC,
        symbol VARCHAR(10));

CREATE TABLE status (
        recommendation VARCHAR(20),
        symbol VARCHAR(10));


#DELETE FROM history WHERE date='2019-10-25';
#delete from live where date > '2019-01-01';
#delete from live;