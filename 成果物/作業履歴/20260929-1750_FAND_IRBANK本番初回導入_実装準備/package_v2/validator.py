"""Preparation v1: exact values, pinned scope and fail-closed quality gates."""
import copy, datetime, decimal, hashlib, json, re, pathlib, stat
VERSION = "production-prep/2"
GATES = tuple("G%02d" % i for i in range(1, 9))
ATTRS = {"actual": "actual", "profit_attribution": "parent_attributable",
         "consolidation": "consolidated", "currency": "JPY"}
class SafeError(Exception):
    def __init__(self, code): self.code = code; super().__init__(code)
def fail(code): raise SafeError(code)
def canonical(x): return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
def digest(x): return hashlib.sha256(canonical(x).encode("utf-8")).hexdigest()
def sha(data): return hashlib.sha256(data).hexdigest()
def exact(raw, scale):
    if not isinstance(raw, str) or not isinstance(scale, str): fail("invalid_value")
    if not re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", raw) or len(raw) > 120: fail("invalid_value")
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", scale) or len(scale)>120: fail("invalid_value")
    with decimal.localcontext() as ctx:
        ctx.prec = 256
        v = decimal.Decimal(raw) * decimal.Decimal(scale)
    if not v.is_finite(): fail("invalid_value")
    return format(v, "f")
def validate_spec(spec):
    if not isinstance(spec, dict) or spec.get("version") != VERSION: fail("input_version_mismatch")
    if spec.get("purpose") != "fixed-first-four-internal-reference": fail("unauthorized_scope")
    if len(spec.get("sources", [])) != 2 or len(spec.get("targets", [])) != 4: fail("unauthorized_scope")
    sources = {s["batch_id"]: s for s in spec["sources"]}
    if len(sources)!=2: fail("unauthorized_scope")
    for s in sources.values():
        if not isinstance(s.get("sha256"),str) or not re.fullmatch("[0-9a-f]{64}",s["sha256"]): fail("input_version_mismatch")
        if type(s.get("size")) is not int or s["size"]<1 or not s.get("source_id"): fail("input_version_mismatch")
    ids, locs, codes, periods = set(),set(),set(),set()
    for t in spec["targets"]:
        if not isinstance(t["entity_id"],str) or not t["entity_id"] or t.get("identifier_scheme")!="approved-string-code": fail("unauthorized_scope")
        try: datetime.date.fromisoformat(t["period"])
        except (ValueError,TypeError): fail("unauthorized_scope")
        if t["metric"]!="net_profit" or t["period_type"]!="annual": fail("unauthorized_scope")
        if t["batch_id"] not in sources or type(t["row"]) is not int or t["row"]<2: fail("input_version_mismatch")
        if not t.get("column") or not t.get("record_id"): fail("input_version_mismatch")
        loc=(t["batch_id"],t["row"],t["column"])
        if loc in locs or t["record_id"] in ids: fail("unauthorized_scope")
        ids.add(t["record_id"]);locs.add(loc);codes.add(t["entity_id"]);periods.add(t["period"])
    if len(codes)!=2 or len(periods)!=2 or {(t["entity_id"],t["period"]) for t in spec["targets"]}!={(e,p) for e in codes for p in periods}: fail("unauthorized_scope")
    for key in ("code_version","schema_version","mapping_version","validation_version","policy_version","designation_version"):
        if not isinstance(spec.get(key),str) or not spec[key]: fail("input_version_mismatch")
    return sources
def business_key(t, evidence):
    return canonical([t["identifier_scheme"],t["entity_id"],t["period"],t["period_type"],t["metric"],
                      evidence.get("profit_attribution",{}).get("effective_value"),
                      evidence.get("consolidation",{}).get("effective_value"),
                      evidence.get("currency",{}).get("effective_value"),t.get("series")])
def check_record(spec, target, record):
    results = {g: ["pass","verified"] for g in GATES}
    def mark(g,state,why): results[g]=[state,why]
    if record.get("record_id")!=target["record_id"] or record.get("source_sha256")!=next(s["sha256"] for s in spec["sources"] if s["batch_id"]==target["batch_id"]):
        mark("G01","reject","input_version_mismatch")
    if record.get("entity_id")!=target["entity_id"]: mark("G02","hold","entity_mismatch")
    if record.get("period")!=target["period"] or record.get("period_type")!="annual": mark("G03","hold","period_mismatch")
    if record.get("metric")!="net_profit": mark("G04","hold","metric_mismatch")
    evidence=record.get("evidence",{})
    for key, value in ATTRS.items():
        ev=evidence.get(key,{})
        valid = (ev.get("source_observation")=="unknown" and ev.get("effective_value")==value
                 and ev.get("evidence_type")==("comparison_and_owner_designation" if key=="currency" else "owner_designation")
                 and ev.get("evidence_ref") and ev.get("evidence_ref")==target.get("evidence",{}).get(key,{}).get("evidence_ref")
                 and canonical(ev)==canonical(target.get("evidence",{}).get(key,{}))
                 and ev.get("designation_version")==spec["designation_version"]
                 and ev.get("applicable_input_version")==record.get("source_sha256")
                 and ev.get("applicable_targets")==[target["record_id"]]
                 and ev.get("purpose")==spec["purpose"])
        if key=="currency":
            proof=ev.get("comparison_proof",{})
            valid=valid and (type(proof) is dict and isinstance(proof.get("sha256"),str)
                  and re.fullmatch("[0-9a-f]{64}",proof["sha256"])
                  and proof.get("input_versions")==sorted(s["sha256"] for s in spec["sources"])
                  and proof.get("targets")==sorted(t["record_id"] for t in spec["targets"])
                  and proof.get("currency")=="JPY" and proof.get("multiplier")=="1" and proof.get("four_exact") is True)
        if not valid: mark("G03" if key=="actual" else "G05" if key=="currency" else "G04","hold","attribute_unconfirmed")
    normalized=None
    if record.get("raw_value") is None:
        mark("G05","hold","missing")
    else:
        try: normalized=exact(record["raw_value"],record.get("scale"))
        except SafeError: mark("G05","reject","invalid_decimal")
    if record.get("scale")!="1" or record.get("raw_unit")!="JPY": mark("G05","hold","unit_unconfirmed")
    if record.get("source_csv_spec_proven") is not False: mark("G07","hold","source_proof_mismatch")
    if not target.get("series") or not target.get("series_evidence"): mark("G06","hold","series_unconfirmed")
    if record.get("row")!=target["row"] or record.get("column")!=target["column"]: mark("G07","hold","position_mismatch")
    state = "reject" if any(v[0]=="reject" for v in results.values()) else "hold" if any(v[0]=="hold" for v in results.values()) else "pass"
    return normalized, results, state
def snapshot(conn):
    tables=("source_batch","processing_run","run_source","entity","staging_fact","validation_record","selection_policy","adoption_candidate")
    out={}
    for table in tables:
        names=[x[1] for x in conn.execute("PRAGMA table_info("+table+")")]
        keep=[n for n in names if n not in ("created_at","content_digest")]
        rows=[dict(zip(keep,row)) for row in conn.execute("SELECT "+",".join(keep)+" FROM "+table)]
        out[table]=sorted(rows,key=canonical)
    return out

def reparse(path):
    try: return bool(pathlib.Path(path).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError,FileNotFoundError): return pathlib.Path(path).is_symlink()
def verify_artifacts(config):
    expected=config.get("artifact_hashes")
    names=("loader.py","reader.py","validator.py","schema.sql")
    if type(expected) is not dict or set(expected)!=set(names): fail("not_ready")
    base=pathlib.Path(__file__).parent
    for name in names:
        p=base/name
        if reparse(p) or sha(p.read_bytes())!=expected[name]: fail("input_version_mismatch")
