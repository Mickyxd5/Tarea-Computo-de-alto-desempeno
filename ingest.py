# ingest.py
import os
import pandas as pd
from elasticsearch import Elasticsearch, helpers
from dateutil import parser

CLOUD_ID = os.getenv("ES_CLOUD_ID")
ES_USER = os.getenv("ES_USER")
ES_PASS = os.getenv("ES_PASS")
INDEX = os.getenv("ES_INDEX", "dataset_index")

def connect():
    print("Conectando a Elasticsearch Cloud...")
    es = Elasticsearch(
        cloud_id=CLOUD_ID,
        basic_auth=(ES_USER, ES_PASS)
    )
    print("Conexión establecida:", es.info().body["cluster_name"])
    return es

def normalize_row(row):
    doc = row.dropna().to_dict()
    if "date" in doc:
        try:
            doc["date"] = parser.parse(str(doc["date"])).isoformat()
        except Exception:
            pass
    return doc

def main(csv_path="dataset/sample.csv"):
    df = pd.read_csv(csv_path)
    print(f"Ingresando {len(df)} filas a {INDEX}...")
    es = connect()

    if not es.indices.exists(index=INDEX):
        es.indices.create(index=INDEX, ignore=400)

    actions = [
        {"_index": INDEX, "_source": normalize_row(row)}
        for _, row in df.iterrows()
    ]

    helpers.bulk(es, actions)
    print("Carga completa en Elasticsearch Cloud.")

if __name__ == "__main__":
    main()
