"""No CLI, no deployment side effects. Caller supplies a pinned, authorized configuration."""
import csv, datetime, io, json, os, pathlib, sqlite3
from validator import *
def verify_config(config, spec, synthetic=False):
    validate_spec(spec)
    if config.get("spec_digest")!=digest(spec): fail("input_version_mismatch")
    if config.get("mode")!="synthetic" or not synthetic:
        if (config.get("mode")!="production" or config.get("production_approved") is not True
            or not config.get("approval_ref") or not config.get("prestart_audit_ref")
            or config.get("deployment_approved") is not True): fail("not_ready")
        verify_artifacts(config)
    if config.get("version")!=VERSION: fail("input_version_mismatch")
def extract_fixed(config,spec):
    verify_config(config,spec)
    records=[]
    for source in spec["sources"]:
        path=pathlib.Path(source["path"])
        if not path.is_absolute() or any(reparse(p) for p in (path,*path.parents)): fail("input_version_mismatch")
        from reader import locked_file
        with locked_file(path):
            data=path.read_bytes()
        if len(data)!=source["size"] or sha(data)!=source["sha256"]: fail("input_version_mismatch")
        try:
            stream=io.StringIO(data.decode(source["encoding"]),newline="")
            parsed=csv.reader(stream)
            header=None
            for index,row in enumerate(parsed,1):
                if index==source["header_record"]:
                    header=row;break
            if header!=source["header"] or len(header)!=len(set(header)): fail("input_version_mismatch")
            reader=csv.DictReader(stream,fieldnames=header)
            fixed={t["row"]:t for t in spec["targets"] if t["batch_id"]==source["batch_id"]}
            for index,row in enumerate(reader,source["header_record"]+1):
                if index not in fixed: continue
                t=fixed[index]
                if None in row or row.get(t["entity_column"])!=t["csv_entity"] or row.get(t["period_column"])!=t["csv_period"]: fail("input_version_mismatch")
                raw=row.get(t["column"])
                rec={k:t[k] for k in ("record_id","entity_id","period","period_type","metric","row","column")}
                rec.update(raw_value=None if raw in source["missing_tokens"] else raw, raw_unit="JPY",scale="1",
                           source_sha256=source["sha256"],source_csv_spec_proven=False,evidence=t["evidence"])
                records.append(rec)
        except (UnicodeError,csv.Error,KeyError): fail("input_version_mismatch")
    if len(records)!=4: fail("input_version_mismatch")
    return records
def prepare(spec, records, policy):
    validate_spec(spec)
    if len(records)!=4 or len({r.get("record_id") for r in records})!=4: fail("unauthorized_scope")
    if policy.get("version")!=spec["policy_version"] or policy.get("purpose")!=spec["purpose"]: fail("input_version_mismatch")
    expected={t["record_id"]:t["batch_id"] for t in spec["targets"]}
    if policy.get("selected_sources")!=expected: fail("input_version_mismatch")
    byid={r["record_id"]:r for r in records}
    if set(byid)!=set(expected): fail("unauthorized_scope")
    for t in spec["targets"]:
        source=next(s for s in spec["sources"] if s["batch_id"]==t["batch_id"])
        if byid[t["record_id"]].get("source_sha256")!=source["sha256"]: fail("input_version_mismatch")
    output=[]
    for t in spec["targets"]:
        rec=byid[t["record_id"]]
        normalized,gates,state=check_record(spec,t,rec)
        output.append([t,rec,normalized,gates,state,business_key(t,rec.get("evidence",{}))])
    # Do not pick first/last/max of equal or conflicting duplicate series.
    groups={}
    for item in output: groups.setdefault(item[5],[]).append(item)
    for group in groups.values():
        if len(group)>1:
            for item in group: item[3]["G06"]=["hold","duplicate_or_series_conflict"];item[4]="hold"
    return output
def load(conn, config, spec, records, policy, schema_text, synthetic=False, created_at=None):
    verify_config(config,spec,synthetic)
    if config.get("schema_sha256")!=sha(schema_text.encode()): fail("input_version_mismatch")
    if conn.in_transaction: fail("integrity_failure")
    conn.execute("PRAGMA foreign_keys=ON")
    items=prepare(spec,records,policy)
    content={"spec":spec,"records":sorted(records,key=lambda r:r["record_id"]),"policy":policy}
    inp=digest(content);run=inp
    exists=conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='processing_run'").fetchone()[0]
    if exists:
        rows=conn.execute("SELECT run_id,input_digest,content_digest FROM processing_run").fetchall()
        if len(rows)!=1 or rows[0][0]!=run or rows[0][1]!=inp: fail("conflict")
        if rows[0][2]!=digest(snapshot(conn)): fail("integrity_failure")
        return {"status":"NOOP","run_id":run}
    # DDL is atomic with inserts: no partially committed candidate state.
    try:
        conn.executescript("BEGIN IMMEDIATE;\n"+schema_text)
        for s in spec["sources"]:
            conn.execute("INSERT INTO source_batch VALUES(?,?,?,?,?)",(s["batch_id"],s["source_id"],s["sha256"],s["size"],spec["version"]))
        state="reject" if any(i[4]=="reject" for i in items) else "hold" if any(i[4]=="hold" for i in items) else "pass"
        versions=[spec[k] for k in ("code_version","schema_version","mapping_version","validation_version","policy_version","designation_version")]
        conn.execute("INSERT INTO processing_run VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                     (run,inp,"pending",*versions,spec["purpose"],state,created_at or datetime.datetime.now(datetime.timezone.utc).isoformat()))
        for s in spec["sources"]: conn.execute("INSERT INTO run_source VALUES(?,?)",(run,s["batch_id"]))
        for e in sorted({t["entity_id"] for t in spec["targets"]}):
            conn.execute("INSERT INTO entity VALUES(?,?,?)",(e,"approved-string-code",e))
        conn.execute("INSERT INTO selection_policy VALUES(?,?,?)",(run,policy["version"],canonical(policy)))
        for t,r,n,gates,state,bkey in items:
            key=canonical([t["row"],t["column"]])
            conn.execute("INSERT INTO staging_fact VALUES("+",".join("?" for _ in range(20))+")",
              (run,t["batch_id"],key,t["record_id"],t["entity_id"],t["period"],t["period_type"],t["metric"],t["row"],t["column"],
               r.get("raw_value"),n,r.get("raw_unit","unknown"),r.get("scale","unknown"),canonical(r.get("evidence",{})),
               t.get("series") or "unknown",bkey,0,state,"missing" if r.get("raw_value") is None else None))
            for gate,(gs,reason) in gates.items():
                conn.execute("INSERT INTO validation_record VALUES(?,?,?,?,?,?,?,?)",
                  (run,t["batch_id"],key,gate,gs,reason,t["record_id"],spec["validation_version"]))
            if state=="pass": conn.execute("INSERT INTO adoption_candidate VALUES(?,?,?,?)",(run,t["batch_id"],key,bkey))
        if conn.execute("PRAGMA foreign_key_check").fetchall(): fail("integrity_failure")
        if conn.execute("SELECT count(*) FROM staging_fact").fetchone()[0]!=4 or conn.execute("SELECT count(*) FROM validation_record").fetchone()[0]!=32: fail("integrity_failure")
        conn.execute("UPDATE processing_run SET content_digest=? WHERE run_id=?",(digest(snapshot(conn)),run))
        conn.commit()
        return {"status":"loaded","run_id":run,"counts":{s:sum(i[4]==s for i in items) for s in ("pass","hold","reject")}}
    except Exception:
        conn.rollback()
        fail("integrity_failure")
def create_first(config,spec,policy,schema_text):
    verify_config(config,spec)
    if config.get("first_load_approved") is not True or not config.get("first_load_approval_ref"): fail("not_ready")
    path=pathlib.Path(config["database_path"])
    if not path.is_absolute() or path.exists() or any(reparse(p) for p in path.parents) or not path.parent.is_dir(): fail("conflict")
    if any(pathlib.Path(str(path)+s).exists() for s in ("-wal","-shm","-journal")): fail("sidecar_present")
    records=extract_fixed(config,spec)
    # Exclusive name reservation. Failure assets are kept; never overwrite or remove.
    fd=os.open(str(path),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
    conn=None
    try:
        conn=sqlite3.connect(path)
        return load(conn,config,spec,records,policy,schema_text)
    except Exception: fail("integrity_failure")
    finally:
        if conn: conn.close()
