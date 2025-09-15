import argparse
import math
import os
import pandas as pd
from elasticsearch import Elasticsearch, helpers

def _to_none_if_nan(x):
    # works for numpy.nan, pandas NA, empty strings, None
    if x is None:
        return None
    if isinstance(x, str):
        s = x.strip()
        return None if s == "" or s.lower() == "nan" else s
    # numeric path
    try:
        # pandas may pass numpy types
        if pd.isna(x):
            return None
    except Exception:
        pass
    return x

def _to_float_safe(x):
    x = _to_none_if_nan(x)
    if x is None:
        return None
    try:
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None

def _get_duration_bucket(duration):
    """Convert duration to 5-second bucket label"""
    if duration is None:
        return "Unknown"
    
    if duration < 5:
        return "0-5 seconds"
    elif duration < 10:
        return "5-10 seconds"
    elif duration < 15:
        return "10-15 seconds"
    elif duration < 20:
        return "15-20 seconds"
    else:
        return "20+ seconds"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to cv-valid-dev.csv (with generated_text column)")
    parser.add_argument("--es", default=os.getenv("NEXT_PUBLIC_ES_HOST", "http://localhost:9200"), help="Elasticsearch URL")
    parser.add_argument("--index", default="cv-transcriptions", help="Destination index")
    args = parser.parse_args()

    es = Elasticsearch(args.es)

    # delete index if exists and recreate - to make this script idempotent.
    if es.indices.exists(index=args.index):
        print(f"Index {args.index} already exists; deleting and recreating")
        es.indices.delete(index=args.index)
    es.indices.create(index=args.index, body={
        "settings": {"number_of_shards": 2, "number_of_replicas": 1},
        "mappings": {
            "properties": {
                "generated_text": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "duration": {"type": "float"},
                "duration_bucket": {"type": "keyword"},
                "age": {"type": "keyword"},
                "gender": {"type": "keyword"},
                "accent": {"type": "keyword"},
                "path": {"type": "keyword"},
                "client_id": {"type": "keyword"},
                # optional extras if present in CSV
                "text": {"type": "text"},
                "up_votes": {"type": "integer"},
                "down_votes": {"type": "integer"}
            }
        }
    })

    df = pd.read_csv(args.csv)
    print(f"df = {df.columns}")

    def to_kw(x):
        x = _to_none_if_nan(x)
        return None if x is None else str(x)

    def gen_actions():
        for _, row in df.iterrows():
            duration = _to_float_safe(row.get("duration"))
            doc = {
                "generated_text": to_kw(row.get("generated_text")),
                "duration": duration,
                "duration_bucket": _get_duration_bucket(duration),
                "age": to_kw(row.get("age")),
                "gender": to_kw(row.get("gender")),
                "accent": to_kw(row.get("accent")),
                "path": to_kw(row.get("path") or row.get("filename") or row.get("file")),
                "client_id": to_kw(row.get("client_id")) if "client_id" in row else None,
                # optional:
                "text": to_kw(row.get("text")),
                "up_votes": None if pd.isna(row.get("up_votes")) else int(row.get("up_votes")),
                "down_votes": None if pd.isna(row.get("down_votes")) else int(row.get("down_votes")),
            }
            # stable _id so re-runs update instead of duplicate
            print(f"doc = {doc}")
            _id = doc["path"] or to_kw(row.get("filename"))
            yield {"_index": args.index, "_id": _id, "_op_type": "index", "_source": doc}

    ok, errors = helpers.bulk(
        es,
        gen_actions(),
        chunk_size=2000,
        request_timeout=120,
        raise_on_error=False
    )
    es.indices.refresh(index=args.index)
    total = es.count(index=args.index)["count"]
    print(f"Indexed/updated: {ok}; total docs now: {total}")
    if errors:
        # show a couple of sample errors so you can adjust the CSV/mapping
        print("Some documents failed to index (showing up to first 3):")
        for e in errors[:3]:
            print(e)


if __name__ == "__main__":
    main()
