PRAGMA foreign_keys=ON;
PRAGMA journal_mode=MEMORY;
CREATE TABLE source_batch(
 batch_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 byte_size INTEGER NOT NULL CHECK(typeof(byte_size)='integer' AND byte_size>0),
 manifest_version TEXT NOT NULL, UNIQUE(source_id,sha256));
CREATE TABLE processing_run(
 run_id TEXT PRIMARY KEY, input_digest TEXT NOT NULL, content_digest TEXT NOT NULL,
 code_version TEXT NOT NULL, schema_version TEXT NOT NULL, mapping_version TEXT NOT NULL,
 validation_version TEXT NOT NULL, policy_version TEXT NOT NULL, designation_version TEXT NOT NULL,
 purpose TEXT NOT NULL CHECK(purpose='fixed-first-four-internal-reference'),
 state TEXT NOT NULL CHECK(state IN ('pass','hold','reject')), created_at TEXT NOT NULL,
 UNIQUE(input_digest,code_version,schema_version,mapping_version,validation_version,policy_version,designation_version,purpose));
CREATE TABLE run_source(
 run_id TEXT NOT NULL, batch_id TEXT NOT NULL, PRIMARY KEY(run_id,batch_id),
 FOREIGN KEY(run_id) REFERENCES processing_run(run_id), FOREIGN KEY(batch_id) REFERENCES source_batch(batch_id));
CREATE TABLE entity(
 entity_id TEXT PRIMARY KEY, identifier_scheme TEXT NOT NULL CHECK(identifier_scheme='approved-string-code'),
 code TEXT NOT NULL CHECK(typeof(code)='text' AND length(code)>0), UNIQUE(identifier_scheme,code));
CREATE TABLE staging_fact(
 run_id TEXT NOT NULL, batch_id TEXT NOT NULL, source_record_key TEXT NOT NULL, record_id TEXT NOT NULL,
 entity_id TEXT NOT NULL, period TEXT NOT NULL, period_type TEXT NOT NULL CHECK(period_type='annual'),
 metric TEXT NOT NULL CHECK(metric='net_profit'), row_number INTEGER NOT NULL CHECK(typeof(row_number)='integer' AND row_number>=2),
 column_name TEXT NOT NULL, raw_value TEXT, normalized_value TEXT, raw_unit TEXT NOT NULL, scale TEXT NOT NULL,
 evidence_json TEXT NOT NULL, series TEXT NOT NULL, business_key TEXT NOT NULL,
 source_csv_spec_proven INTEGER NOT NULL CHECK(source_csv_spec_proven=0),
 state TEXT NOT NULL CHECK(state IN ('pass','hold','reject')), missing_reason TEXT,
 CHECK((raw_value IS NULL AND normalized_value IS NULL AND missing_reason IS NOT NULL) OR raw_value IS NOT NULL),
 PRIMARY KEY(run_id,batch_id,source_record_key), UNIQUE(run_id,record_id),
 FOREIGN KEY(run_id,batch_id) REFERENCES run_source(run_id,batch_id), FOREIGN KEY(entity_id) REFERENCES entity(entity_id));
CREATE TABLE validation_record(
 run_id TEXT NOT NULL,batch_id TEXT NOT NULL,source_record_key TEXT NOT NULL,
 gate_id TEXT NOT NULL CHECK(gate_id IN ('G01','G02','G03','G04','G05','G06','G07','G08')),
 state TEXT NOT NULL CHECK(state IN ('pass','hold','reject')), reason TEXT NOT NULL, evidence_ref TEXT NOT NULL,
 validation_version TEXT NOT NULL, PRIMARY KEY(run_id,batch_id,source_record_key,gate_id),
 FOREIGN KEY(run_id,batch_id,source_record_key) REFERENCES staging_fact(run_id,batch_id,source_record_key));
CREATE TABLE selection_policy(
 run_id TEXT PRIMARY KEY, policy_version TEXT NOT NULL, policy_json TEXT NOT NULL,
 FOREIGN KEY(run_id) REFERENCES processing_run(run_id));
CREATE TABLE adoption_candidate(
 run_id TEXT NOT NULL,batch_id TEXT NOT NULL,source_record_key TEXT NOT NULL,
 business_key TEXT NOT NULL, PRIMARY KEY(run_id,batch_id,source_record_key), UNIQUE(run_id,business_key),
 FOREIGN KEY(run_id,batch_id,source_record_key) REFERENCES staging_fact(run_id,batch_id,source_record_key));
