"""Fixed-contract reader; never accepts a database path from a request."""
import contextlib, ctypes, json, os, pathlib, sqlite3
from validator import *
CONTRACT="irbank-performance-production/1"
KEYS={"schema_version","request_id","request_type","entity_ids","periods","metric","limit"}
TABLES={"source_batch","processing_run","run_source","entity","staging_fact","validation_record","selection_policy","adoption_candidate","sqlite_master"}
def parse_request(text):
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result: fail("invalid_request")
            result[key]=value
        return result
    try: return json.loads(text,object_pairs_hook=unique,parse_constant=lambda x:fail("invalid_request"))
    except SafeError: raise
    except Exception: fail("invalid_request")
def request_valid(request,spec):
    if type(request) is not dict or set(request)!=KEYS: fail("invalid_request")
    if request["schema_version"]!=CONTRACT or request["request_type"]!="get_company_performance" or request["metric"]!="net_profit": fail("invalid_request")
    rid=request["request_id"]
    if not isinstance(rid,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",rid): fail("invalid_request")
    if type(request["limit"]) is not int or not 1<=request["limit"]<=4: fail("invalid_request")
    for key,allowed in (("entity_ids",{t["entity_id"] for t in spec["targets"]}),("periods",{t["period"] for t in spec["targets"]})):
        values=request[key]
        if type(values) is not list or not 1<=len(values)<=2 or any(type(v) is not str for v in values): fail("invalid_request")
        if len(set(values))!=len(values): fail("invalid_request")
        if not set(values)<=allowed: fail("unauthorized_scope")
def authorizer(action,a,b,db,trigger):
    if action==sqlite3.SQLITE_SELECT: return sqlite3.SQLITE_OK
    if action==sqlite3.SQLITE_READ and a in TABLES: return sqlite3.SQLITE_OK
    if action==sqlite3.SQLITE_FUNCTION and b in {"count"}: return sqlite3.SQLITE_OK
    if action==sqlite3.SQLITE_PRAGMA and a in {"table_info","foreign_key_check","integrity_check","query_only"} and (a!="query_only" or b is None): return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY
def verify_database(conn,config,spec):
    validate_spec(spec)
    if config.get("spec_digest")!=digest(spec): fail("input_version_mismatch")
    if conn.execute("PRAGMA foreign_key_check").fetchall() or conn.execute("PRAGMA integrity_check").fetchone()[0]!="ok": fail("integrity_failure")
    if {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}!=TABLES-{"sqlite_master"}: fail("integrity_failure")
    rows=conn.execute("SELECT run_id,input_digest,content_digest,code_version,schema_version,mapping_version,validation_version,policy_version,designation_version,purpose,state FROM processing_run").fetchall()
    if len(rows)!=1: fail("integrity_failure")
    row=rows[0]
    versions=tuple(spec[k] for k in ("code_version","schema_version","mapping_version","validation_version","policy_version","designation_version","purpose"))
    if tuple(row[3:10])!=versions or row[0]!=row[1]: fail("input_version_mismatch")
    if row[2]!=digest(snapshot(conn)): fail("integrity_failure")
    sources=conn.execute("SELECT batch_id,source_id,sha256,byte_size,manifest_version FROM source_batch ORDER BY batch_id").fetchall()
    expected=sorted((s["batch_id"],s["source_id"],s["sha256"],s["size"],spec["version"]) for s in spec["sources"])
    if sources!=expected: fail("input_version_mismatch")
    if conn.execute("SELECT count(*) FROM run_source WHERE run_id=?",(row[0],)).fetchone()[0]!=2: fail("integrity_failure")
    if conn.execute("SELECT count(*) FROM staging_fact").fetchone()[0]!=4 or conn.execute("SELECT count(*) FROM validation_record").fetchone()[0]!=32: fail("integrity_failure")
    policy=conn.execute("SELECT policy_version,policy_json FROM selection_policy WHERE run_id=?",(row[0],)).fetchone()
    if not policy or policy[0]!=spec["policy_version"]: fail("input_version_mismatch")
    pobj=json.loads(policy[1])
    if pobj.get("selected_sources")!={t["record_id"]:t["batch_id"] for t in spec["targets"]} or pobj.get("purpose")!=spec["purpose"]: fail("input_version_mismatch")
    targets={t["record_id"]:t for t in spec["targets"]}
    fields="run_id,batch_id,source_record_key,record_id,entity_id,period,period_type,metric,row_number,column_name,raw_value,normalized_value,raw_unit,scale,evidence_json,series,business_key,source_csv_spec_proven,state,missing_reason"
    facts=conn.execute("SELECT "+fields+" FROM staging_fact").fetchall()
    for fact in facts:
        if fact[3] not in targets: fail("integrity_failure")
        t=targets[fact[3]]
        if fact[0]!=row[0] or fact[1]!=t["batch_id"] or fact[2]!=canonical([t["row"],t["column"]]) or tuple(fact[4:10])!=(t["entity_id"],t["period"],t["period_type"],t["metric"],t["row"],t["column"]): fail("integrity_failure")
        ev=json.loads(fact[14])
        rec={"record_id":t["record_id"],"entity_id":fact[4],"period":fact[5],"period_type":fact[6],"metric":fact[7],
             "row":fact[8],"column":fact[9],"raw_value":fact[10],"raw_unit":fact[12],"scale":fact[13],
             "source_sha256":next(s["sha256"] for s in spec["sources"] if s["batch_id"]==t["batch_id"]),
             "source_csv_spec_proven":False if fact[17]==0 else True,"evidence":ev}
        norm,gates,state=check_record(spec,t,rec)
        if norm!=fact[11] or business_key(t,ev)!=fact[16]: fail("integrity_failure")
        gates_db=conn.execute("SELECT gate_id,state,reason,validation_version FROM validation_record WHERE run_id=? AND batch_id=? AND source_record_key=?",fact[:3]).fetchall()
        if {g[0] for g in gates_db}!=set(GATES) or any(g[3]!=spec["validation_version"] for g in gates_db): fail("integrity_failure")
        # Stored hold/reject must not be promoted to a passing candidate.
        candidate=conn.execute("SELECT business_key FROM adoption_candidate WHERE run_id=? AND batch_id=? AND source_record_key=?",fact[:3]).fetchone()
        if candidate and (state!="pass" or fact[18]!="pass" or any(g[1]!="pass" for g in gates_db) or candidate[0]!=fact[16]): fail("integrity_failure")
        if fact[18]=="pass" and not candidate: fail("integrity_failure")
    return row[0]
def query_connection(conn,request,config,spec,synthetic=False):
    request_valid(request,spec)
    if not synthetic or config.get("mode")!="synthetic":
        if config.get("ready") is not True or config.get("production_approved") is not True or not config.get("completion_audit_ref") or not config.get("activation_approval_ref"): fail("not_ready")
        if config.get("version")!=VERSION: fail("input_version_mismatch")
        verify_artifacts(config)
    conn.execute("PRAGMA query_only=ON")
    conn.set_authorizer(authorizer)
    try:
        run=verify_database(conn,config,spec)
        placeholders=lambda values:",".join("?" for _ in values)
        sql=("SELECT s.record_id,s.entity_id,s.period,s.metric,s.raw_value,s.normalized_value,s.evidence_json,s.scale,s.source_csv_spec_proven,s.state,c.source_record_key "
             "FROM staging_fact s LEFT JOIN adoption_candidate c ON s.run_id=c.run_id AND s.batch_id=c.batch_id AND s.source_record_key=c.source_record_key "
             "WHERE s.run_id=? AND s.entity_id IN ("+placeholders(request["entity_ids"])+") AND s.period IN ("+placeholders(request["periods"])+") ORDER BY s.entity_id,s.period,s.record_id")
        rows=conn.execute(sql,(run,*request["entity_ids"],*request["periods"])).fetchall()
        values=[];availability=[]
        found={(r[1],r[2]) for r in rows}
        for r in rows:
            if r[10] is None:
                reasons=conn.execute("SELECT reason FROM validation_record v JOIN staging_fact s ON v.run_id=s.run_id AND v.batch_id=s.batch_id AND v.source_record_key=s.source_record_key WHERE s.run_id=? AND s.record_id=? AND v.state!='pass' ORDER BY v.gate_id",(run,r[0])).fetchall()
                availability.append({"entity_id":r[1],"period":r[2],"reason":r[9],"details":[x[0] for x in reasons]})
                continue
            values.append({"record_id":r[0],"entity_id":r[1],"period":r[2],"metric":r[3],"raw_value":r[4],
                           "decimal_value":r[5],"evidence":json.loads(r[6]),"currency_scale":r[7],
                           "source_csv_spec_proven":False,"quality":"quality_pass"})
        for e in sorted(request["entity_ids"]):
            for p in sorted(request["periods"]):
                if (e,p) not in found: availability.append({"entity_id":e,"period":p,"reason":"absent"})
        return {"schema_version":CONTRACT,"request_id":request["request_id"],"run_id":run,
                "source_versions":[{"batch_id":s["batch_id"],"sha256":s["sha256"]} for s in spec["sources"]],
                "versions":{k:spec[k] for k in ("version","mapping_version","validation_version","policy_version","designation_version")},
                "target_count":len(rows),"candidate_count":len(values),"returned_count":min(len(values),request["limit"]),
                "truncated":len(values)>request["limit"],"records":values[:request["limit"]],"availability":availability}
    except SafeError: raise
    except Exception: fail("integrity_failure")
@contextlib.contextmanager
def locked_file(path):
    """Windows share-read only for the entire SQLite session; excludes write/delete."""
    p=pathlib.Path(path)
    if not p.is_absolute() or any(reparse(parent) for parent in (p,*p.parents)): fail("integrity_failure")
    if os.name!="nt": fail("not_ready")
    kernel=ctypes.WinDLL("kernel32",use_last_error=True)
    kernel.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p]
    kernel.CreateFileW.restype=ctypes.c_void_p
    handle=kernel.CreateFileW(str(p),0x80000000,1,None,3,0x80,None)
    if handle==ctypes.c_void_p(-1).value: fail("not_ready")
    try: yield p
    finally:
        kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.CloseHandle(handle)
def read(request,config,spec):
    try:
        if isinstance(request,str): request=parse_request(request)
        request_valid(request,spec)
        if config.get("ready") is not True or not config.get("database_path") or not config.get("database_sha256") or not config.get("completion_audit_ref") or not config.get("activation_approval_ref"): fail("not_ready")
        with locked_file(config["database_path"]) as p:
            if any(pathlib.Path(str(p)+s).exists() for s in ("-wal","-shm","-journal")): fail("sidecar_present")
            if sha(p.read_bytes())!=config["database_sha256"]: fail("input_version_mismatch")
            conn=sqlite3.connect(p.as_uri()+"?mode=ro&immutable=1",uri=True)
            try: return query_connection(conn,request,config,spec)
            finally: conn.close()
    except SafeError as exc: return {"error":exc.code,"message":exc.code}
    except Exception: return {"error":"integrity_failure","message":"integrity_failure"}
