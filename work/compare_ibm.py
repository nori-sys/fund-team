import sqlite3,csv,datetime
db=sqlite3.connect('file:database/fund_stock.db?mode=ro&immutable=1',uri=True)
csvpath=r'C:\fchart\usa\ibm.csv'
rows=[]
with open(csvpath,encoding='utf-8-sig') as f:
    rd=csv.reader(f); next(rd); next(rd)
    for r in rd:
        if len(r)>=6:
            try:
                d=datetime.datetime.strptime(r[0],'%y%m%d').date().isoformat(); rows.append((d,)+tuple(float(x) for x in r[1:5])+(int(float(r[-1])),))
            except (ValueError,IndexError):
                continue
print('csv_rows',len(rows),'range',rows[0][0],rows[-1][0])
unknown=[r[0] for r in db.execute("select fchart_code from stocks where security_name like 'UNKNOWN_%'")]
for code in unknown:
    dbrows=db.execute('select trade_date,open,high,low,close,volume from daily_prices_raw where fchart_code=?',(code,)).fetchall()
    mp={r[0]:r[1:] for r in dbrows}; matches=0; compared=0; exact=0; scale=[]
    for r in rows:
        if r[0] in mp:
            compared+=1; a=mp[r[0]]; b=r[1:]
            if a==b: exact+=1
            ratios=[a[i]/b[i] for i in range(4) if b[i]]
            if ratios and max(ratios)-min(ratios)<0.01: scale.append(round(ratios[0],4))
    if exact or compared>=5:
        print('candidate',code,'db_rows',len(dbrows),'compared',compared,'exact',exact,'scales',sorted(set(scale))[:10])
