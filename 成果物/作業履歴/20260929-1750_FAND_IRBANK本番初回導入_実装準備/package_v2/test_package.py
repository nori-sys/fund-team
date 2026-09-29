"""Synthetic-only tests. In-memory DB unless explicitly called for approved sidecar test."""
import copy, json, pathlib, sqlite3, unittest
import loader, reader, validator
from validator import SafeError
def resources():
    base=pathlib.Path(__file__).parent
    return json.loads((base/"synthetic_fixture.json").read_text(encoding="utf-8")), (base/"schema.sql").read_text(encoding="utf-8")
class PackageTests(unittest.TestCase):
    def setUp(self):
        self.fx,self.schema=resources();self.spec=self.fx["spec"]
        self.cfg={"mode":"synthetic","version":validator.VERSION,"spec_digest":validator.digest(self.spec),"schema_sha256":validator.sha(self.schema.encode())}
    def db(self,fx=None):
        f=fx or self.fx;c=sqlite3.connect(":memory:")
        cfg=dict(self.cfg,spec_digest=validator.digest(f["spec"]))
        result=loader.load(c,cfg,f["spec"],f["records"],f["policy"],self.schema,synthetic=True)
        return c,cfg,result
    def req(self):
        return {"schema_version":reader.CONTRACT,"request_id":"SYN-test","request_type":"get_company_performance",
                "entity_ids":["SYN001","SYN002"],"periods":["2000-03-31","2001-03-31"],"metric":"net_profit","limit":4}
    def test_four_thirtytwo_fk_constraints(self):
        c,cfg,r=self.db()
        self.assertEqual(r["counts"],{"pass":4,"hold":0,"reject":0})
        self.assertEqual(c.execute("SELECT count(*) FROM validation_record").fetchone()[0],32)
        self.assertFalse(c.execute("PRAGMA foreign_key_check").fetchall())
        self.assertEqual(c.execute("PRAGMA integrity_check").fetchone()[0],"ok")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO run_source VALUES('bad','bad')")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("UPDATE staging_fact SET state='accepted'")
        c.rollback();c.close()
    def test_exact_zero_negative_precision_evidence(self):
        c,cfg,r=self.db()
        out=reader.query_connection(c,self.req(),cfg,self.spec,synthetic=True)
        self.assertEqual([x["decimal_value"] for x in out["records"]],["0","-12","9007199254740993","1.25"])
        self.assertTrue(all(x["source_csv_spec_proven"] is False and x["evidence"]["actual"]["source_observation"]=="unknown" for x in out["records"]))
        c.close()
        self.assertEqual(validator.exact("123.45","1000"),"123450.00")
        self.assertEqual(validator.exact("123456789012345678901234567890","1000000"),"123456789012345678901234567890000000")
    def test_missing_invalid_unknown_hold_no_return(self):
        for change in ("missing","invalid","attribute","unit","position","entity","period","metric","series","proof"):
            f=copy.deepcopy(self.fx)
            r=f["records"][0]
            if change=="missing": r["raw_value"]=None
            if change=="invalid": r["raw_value"]="NaN"
            if change=="attribute": r["evidence"]["consolidation"]["effective_value"]="unknown"
            if change=="unit": r["scale"]="1000"
            if change=="position": r["row"]=999
            if change=="entity": r["entity_id"]="OTHER"
            if change=="period": r["period"]="2099-03-31"
            if change=="metric": r["metric"]="sales"
            if change=="series": f["spec"]["targets"][0]["series_evidence"]=""
            if change=="proof": r["source_csv_spec_proven"]=True
            c,cfg,result=self.db(f)
            self.assertEqual(c.execute("SELECT count(*) FROM staging_fact").fetchone()[0],4)
            self.assertEqual(c.execute("SELECT count(*) FROM adoption_candidate").fetchone()[0],3)
            # Reader must reject corrupt source claims or leave failed record unavailable.
            if change in ("position","entity","period","metric","proof"):
                # The immutable staged identity is target-fixed, never corrected into a candidate.
                self.assertEqual(c.execute("SELECT state FROM staging_fact WHERE record_id='SYN-0-0'").fetchone()[0] in ("hold","reject"),True)
            else:
                out=reader.query_connection(c,self.req(),cfg,f["spec"],synthetic=True)
                self.assertEqual(out["returned_count"],3)
                self.assertEqual(len(out["availability"]),1)
            c.close()
    def test_request_injection_type_duplicates_unknown_keys(self):
        base=self.req()
        variants=[dict(base,limit=True),dict(base,limit=0),dict(base,limit=5),dict(base,limit=1.0),
                  dict(base,entity_ids=["SYN001","SYN001"]),dict(base,entity_ids=[1]),dict(base,entity_ids=[]),
                  dict(base,entity_ids=["SYN001' OR 1=1 --"]),dict(base,periods=[None]),
                  dict(base,periods=["2000-03-31","2000-03-31"]),dict(base,metric="sales"),
                  dict(base,database_path="anything"),dict(base,sql="ATTACH DATABASE"),dict(base,request_id="bad\nid"),
                  dict(base,schema_version="irbank-performance-poc/1"),None]
        for request in variants:
            with self.assertRaises(SafeError): reader.request_valid(request,self.spec)
    def test_versions_sha_scope_and_preparation_rejection(self):
        with self.assertRaises(SafeError): loader.extract_fixed(self.cfg,self.spec)
        with self.assertRaises(SafeError): loader.create_first(self.cfg,self.spec,self.fx["policy"],self.schema)
        self.assertEqual(reader.read(self.req(),self.cfg,self.spec)["error"],"not_ready")
        f=copy.deepcopy(self.fx);f["spec"]["sources"][0]["sha256"]="c"*64
        c=sqlite3.connect(":memory:")
        with self.assertRaises(SafeError): loader.load(c,self.cfg,f["spec"],f["records"],f["policy"],self.schema,synthetic=True)
        self.assertEqual(c.execute("SELECT count(*) FROM sqlite_master").fetchone()[0],0);c.close()
        f=copy.deepcopy(self.fx);f["records"][0]["source_sha256"]="c"*64
        with self.assertRaises(SafeError): self.db(f)
        f=copy.deepcopy(self.fx);f["spec"]["targets"][0]["row"]=True
        with self.assertRaises(SafeError): validator.validate_spec(f["spec"])
    def test_noop_timestamp_exclusion_no_overwrite_conflict(self):
        c,cfg,r=self.db();before=validator.digest(validator.snapshot(c))
        result=loader.load(c,cfg,self.spec,self.fx["records"],self.fx["policy"],self.schema,synthetic=True,created_at="different-time")
        self.assertEqual(result["status"],"NOOP");self.assertEqual(before,validator.digest(validator.snapshot(c)))
        c.execute("UPDATE processing_run SET created_at='another-time'");c.commit()
        self.assertEqual(before,validator.digest(validator.snapshot(c)))
        f=copy.deepcopy(self.fx);f["records"][0]["raw_value"]="99"
        with self.assertRaises(SafeError): loader.load(c,cfg,self.spec,f["records"],f["policy"],self.schema,synthetic=True)
        self.assertEqual(before,validator.digest(validator.snapshot(c)));c.close()
    def test_reader_tamper_versions_gates_policy(self):
        for query in ("UPDATE staging_fact SET normalized_value='99'","UPDATE validation_record SET state='hold' WHERE gate_id='G01'",
                      "UPDATE processing_run SET mapping_version='other'","DELETE FROM validation_record WHERE gate_id='G08'",
                      "UPDATE selection_policy SET policy_json='{}'","DELETE FROM adoption_candidate"):
            c,cfg,r=self.db();c.execute(query);c.commit()
            with self.assertRaises(SafeError): reader.query_connection(c,self.req(),cfg,self.spec,synthetic=True)
            c.close()
    def test_deterministic_limit_queryonly_authorizer(self):
        c,cfg,r=self.db();req=dict(self.req(),limit=1)
        out=reader.query_connection(c,req,cfg,self.spec,synthetic=True)
        self.assertEqual((out["target_count"],out["returned_count"],out["truncated"]),(4,1,True))
        for q in ("UPDATE staging_fact SET raw_value='9'","ATTACH DATABASE ':memory:' AS extra","PRAGMA query_only=OFF","DROP TABLE entity"):
            with self.assertRaises(sqlite3.DatabaseError): c.execute(q)
        c.close()
    def test_pinned_attribute_refs_comparison_proof(self):
        for attr in ("actual","profit_attribution","consolidation","currency"):
            f=copy.deepcopy(self.fx);f["records"][0]["evidence"][attr]["evidence_ref"]="SYN-unapproved"
            c,cfg,r=self.db(f);self.assertEqual(r["counts"]["hold"],1)
            self.assertEqual(reader.query_connection(c,self.req(),cfg,f["spec"],synthetic=True)["returned_count"],3);c.close()
        for mutation in ("owner-only","absent-proof","wrong-sha","wrong-input","wrong-target","not-exact"):
            f=copy.deepcopy(self.fx);ev=f["records"][0]["evidence"]["currency"]
            if mutation=="owner-only":ev["evidence_type"]="owner_designation"
            if mutation=="absent-proof":ev.pop("comparison_proof")
            if mutation=="wrong-sha":ev["comparison_proof"]["sha256"]="d"*64
            if mutation=="wrong-input":ev["comparison_proof"]["input_versions"]=["e"*64]
            if mutation=="wrong-target":ev["comparison_proof"]["targets"]=["SYN-other"]
            if mutation=="not-exact":ev["comparison_proof"]["four_exact"]=False
            c,cfg,r=self.db(f);self.assertEqual(r["counts"]["hold"],1)
            self.assertEqual(reader.query_connection(c,self.req(),cfg,f["spec"],synthetic=True)["returned_count"],3);c.close()
        # A missing comparison even in the pinned target remains unknown, never pass.
        f=copy.deepcopy(self.fx);f["records"][0]["evidence"]["currency"].pop("comparison_proof")
        f["spec"]["targets"][0]["evidence"]["currency"].pop("comparison_proof")
        c,cfg,r=self.db(f);self.assertEqual(r["counts"]["hold"],1);c.close()
    def test_json_duplicate_keys_and_atomic_failure(self):
        with self.assertRaises(SafeError): reader.parse_request('{"limit":1,"limit":2}')
        with self.assertRaises(SafeError): reader.parse_request('{"limit":NaN}')
        c=sqlite3.connect(":memory:")
        bad_schema=self.schema.replace("CREATE TABLE entity","CREATE TABLE entityBROKEN")
        cfg=dict(self.cfg,schema_sha256=validator.sha(bad_schema.encode()))
        with self.assertRaises(SafeError): loader.load(c,cfg,self.spec,self.fx["records"],self.fx["policy"],bad_schema,synthetic=True)
        self.assertEqual(c.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0],0)
        c.close()
    def test_selection_not_implicit_duplicates(self):
        f=copy.deepcopy(self.fx);f["policy"]["selected_sources"].pop("SYN-0-0")
        c=sqlite3.connect(":memory:")
        with self.assertRaises(SafeError): loader.load(c,self.cfg,self.spec,f["records"],f["policy"],self.schema,synthetic=True)
        c.close()
        f=copy.deepcopy(self.fx);f["records"][1]["record_id"]=f["records"][0]["record_id"]
        with self.assertRaises(SafeError): loader.prepare(f["spec"],f["records"],f["policy"])
        # Unknown series holds even if numerical values match.
        f=copy.deepcopy(self.fx);f["spec"]["targets"][0]["series"]=None;f["records"][0]["raw_value"]="0"
        c,cfg,r=self.db(f);self.assertEqual(r["counts"]["hold"],1);c.close()
def file_tests(database_path):
    """Only the caller's authorized synthetic filename. Never allocates other names."""
    f,schema=resources()
    p=pathlib.Path(database_path)
    if p.name!="production_prep_synthetic_reader_v2.sqlite" or p.exists(): raise AssertionError("collision")
    cfg={"mode":"synthetic","version":validator.VERSION,"spec_digest":validator.digest(f["spec"]),"schema_sha256":validator.sha(schema.encode())}
    mem=sqlite3.connect(":memory:");loader.load(mem,cfg,f["spec"],f["records"],f["policy"],schema,synthetic=True)
    with p.open("xb") as out: out.write(mem.serialize())
    mem.close()
    request=PackageTests().req()
    ready=dict(cfg,mode="production",ready=True,production_approved=True,completion_audit_ref="synthetic-test-only",
               activation_approval_ref="synthetic-test-only",database_path=str(p),database_sha256=validator.sha(p.read_bytes()),
               artifact_hashes={n:validator.sha((pathlib.Path(__file__).parent/n).read_bytes()) for n in ("loader.py","reader.py","validator.py","schema.sql")})
    success=reader.read(request,ready,f["spec"])
    assert success["returned_count"]==4
    with reader.locked_file(p):
        try:
            with p.open("r+b"): pass
        except PermissionError: pass
        else: raise AssertionError("write sharing was allowed")
    ro=sqlite3.connect(p.as_uri()+"?mode=ro&immutable=1",uri=True)
    try:
        try: ro.execute("UPDATE entity SET code='modified'")
        except sqlite3.OperationalError: pass
        else: raise AssertionError("read-only write allowed")
    finally: ro.close()
    for suffix in ("-wal","-shm","-journal"): assert not pathlib.Path(str(p)+suffix).exists()
    wal=pathlib.Path(str(p)+"-wal")
    with wal.open("xb") as out: out.write(b"SYNTHETIC-SIDECAR-REJECTION-ONLY")
    rejected=reader.read(request,ready,f["spec"])
    assert rejected["error"]=="sidecar_present"
    return {"ro_immutable":True,"query_only":True,"sharing_write_rejected":True,"sidecar_rejected":True,"preserved_files":2}
if __name__=="__main__": unittest.main()
