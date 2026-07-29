import sqlite3, pathlib
db='file:database/fund_stock.db?mode=ro&immutable=1'
c=sqlite3.connect(db, uri=True)
def q(s,*a): return c.execute(s,a).fetchall()
print('tables',q("select name from sqlite_master where type='table'"))
for t in ['stocks','daily_prices_raw','daily_prices_adjusted','import_files','validation_results']:
 print('count',t,q(f'select count(*) from {t}')[0][0])
print('date_range',q('select min(trade_date),max(trade_date) from daily_prices_raw')[0])
print('unknown_count',q("select count(*) from stocks where security_name like 'UNKNOWN_%'")[0][0])
rows=q('''select s.fchart_code,s.security_name,min(d.trade_date),max(d.trade_date),count(d.trade_date),sum(case when d.trade_date=(select max(trade_date) from daily_prices_raw) then 1 else 0 end) from stocks s left join daily_prices_raw d using(fchart_code) where s.security_name like 'UNKNOWN_%' group by s.fchart_code order by s.fchart_code''')
print('unknown sample',rows[:5]); print('unknown rows',len(rows))
print('unknown latest_flag',q('select sum(case when last_date=(select max(trade_date) from daily_prices_raw) then 1 else 0 end),sum(case when last_date is null then 1 else 0 end) from (select s.fchart_code,max(d.trade_date) last_date from stocks s left join daily_prices_raw d using(fchart_code) where s.security_name like "UNKNOWN_%" group by s.fchart_code)')[0])
print('unknown count buckets',q('select case when count(d.trade_date)=0 then "0" when count(d.trade_date)<10 then "1-9" when count(d.trade_date)<100 then "10-99" when count(d.trade_date)<1000 then "100-999" else "1000+" end b,count(*) from stocks s left join daily_prices_raw d using(fchart_code) where s.security_name like "UNKNOWN_%" group by s.fchart_code')[0:10])
print('integrity',q('pragma integrity_check'))
print('ohlc',q('select count(*) from daily_prices_raw where high<open or high<close or high<low or low>open or low>close or low>high or volume<0')[0][0])
k=next(pathlib.Path('.').rglob('kabu.lst'))
codes=set()
for line in k.read_text(encoding='cp932').splitlines():
 try: codes.add(int(line.split(',')[0]))
 except: pass
dbcodes={r[0] for r in q('select fchart_code from stocks')}
print('kabu_path',k,'kabu_rows',len(codes),'matched_stocks',len(codes&dbcodes),'unmatched_kabu',len(codes-dbcodes),'db_not_kabu',len(dbcodes-codes),'success_rate_vs_kabu',len(codes&dbcodes)/len(codes))
print('latest_unknowns',q("select s.fchart_code,min(d.trade_date),max(d.trade_date),count(*),min(d.source_fxx),max(d.source_fxx) from stocks s join daily_prices_raw d using(fchart_code) where s.security_name like 'UNKNOWN_%' group by s.fchart_code having max(d.trade_date)='2026-07-16' order by s.fchart_code"))
