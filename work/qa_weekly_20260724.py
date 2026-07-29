import sqlite3
c=sqlite3.connect('file:database/fund_stock.db?mode=ro&immutable=1',uri=True)
def one(s): return c.execute(s).fetchone()[0]
print('integrity',c.execute('pragma integrity_check').fetchone()[0])
print('daily_count',one('select count(*) from daily_prices_raw'))
print('weekly_count',one("select count(*) from weekly_prices where timeframe_code='1W'"))
print('weekly_dup',one("select count(*) from (select fchart_code,timeframe_code,period_start,count(*) c from weekly_prices group by fchart_code,timeframe_code,period_start having c>1)"))
print('weekly_ohlc',one("select count(*) from weekly_prices where high<open or high<close or high<low or low>open or low>close or low>high or volume<0"))
print('nulls',one("select count(*) from weekly_prices where open is null or high is null or low is null or close is null or volume is null"))
q='''WITH g AS (SELECT fchart_code,date(trade_date, '-' || ((CAST(strftime('%w',trade_date) AS INTEGER)+6)%7) || ' days') ps,MIN(trade_date) fd,MAX(trade_date) ld,MAX(high) hi,MIN(low) lo,SUM(volume) vo FROM daily_prices_raw GROUP BY fchart_code,ps)
SELECT count(*) FROM g JOIN weekly_prices w ON w.fchart_code=g.fchart_code AND w.period_start=g.ps AND w.timeframe_code='1W' JOIN daily_prices_raw d1 ON d1.fchart_code=g.fchart_code AND d1.trade_date=g.fd JOIN daily_prices_raw d2 ON d2.fchart_code=g.fchart_code AND d2.trade_date=g.ld WHERE w.open<>d1.open OR w.high<>g.hi OR w.low<>g.lo OR w.close<>d2.close OR w.volume<>g.vo'''
print('mismatch',one(q))
print('timeframe',c.execute("select * from timeframes where timeframe_code='1W'").fetchone())
