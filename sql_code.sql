-- Create Database

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


-- DELETE FROM history WHERE date='2019-10-25';
-- delete from live where date > '2019-01-01';
-- delete from live;


-- ['BLL','CMG','AEP','DTE','TDG','EW','DUK','AMZN','KEYS','AAPL','BA','FORD','MSFT','ETR','RSG','AMD','NEE']
['BLL','CMG','AEP','DTE','TDG','EW','DUK','KEYS','MSFT','ETR','RSG','AMD','NEE']


--select symbol, adjclose from history where symbol in ('AAPL','AMZN') and date = (select max(date) from history);
select * from live where (symbol, date) in (select symbol, max(date) from live group by symbol);

-- select date,symbol,adjclose from history where symbol in ('AAPL','AMZN') and date in (select max(date) from history group by symbol);

-- insert into status values ('BUY','BLL');
-- insert into status values ('BUY','CMG');
-- insert into status values ('BUY','AEP');
-- insert into status values ('BUY','DTE');
-- insert into status values ('BUY','TDG');
-- insert into status values ('BUY','EW');
-- insert into status values ('BUY','DUK');
-- insert into status values ('BUY','KEYS');
-- insert into status values ('BUY','MSFT');
-- insert into status values ('BUY','ETR');
-- insert into status values ('BUY','RSG');
-- insert into status values ('BUY','AMD');
-- insert into status values ('BUY','NEE');


insert into live values ('2019-10-25 14:41:10',100.00,'MSFT');
insert into live values ('2019-10-25 14:41:10',101.01,'BLL');
insert into live values ('2019-10-25 14:41:10',102.02,'CMG');
insert into live values ('2019-10-25 14:41:10',103.03,'AEP');
insert into live values ('2019-10-25 14:41:10',104.04,'DTE');
insert into live values ('2019-10-25 14:41:10',105.05,'TDG');
insert into live values ('2019-10-25 14:41:10',106.06,'EW');
insert into live values ('2019-10-25 14:41:10',107.07,'DUK');
insert into live values ('2019-10-25 14:41:10',108.08,'KEYS');
insert into live values ('2019-10-25 14:41:10',109.09,'ETR');
insert into live values ('2019-10-25 14:41:10',110.10,'RSG');
insert into live values ('2019-10-25 14:41:10',111.11,'AMD');
insert into live values ('2019-10-25 14:41:10',112.12,'NEE');

DELETE FROM live WHERE date < '2019-10-27 14:41:09';

stocks_to_track = ['BLL','CMG','AEP','DTE','TDG','EW','DUK','KEYS','ETR','RSG','AMD','NEE']

select * from status where symbol = 'EW';

delete from status where symbol='EW';
insert into status values ('BUY','EW');


delete from status where symbol='EW';
insert into status values ('SELL','EW');