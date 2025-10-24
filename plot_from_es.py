# plot_from_es.py
import os
import pandas as pd
from elasticsearch import Elasticsearch
import plotly.express as px

CLOUD_ID = os.getenv("ES_CLOUD_ID")
ES_USER = os.getenv("ES_USER")
ES_PASS = os.getenv("ES_PASS")
INDEX = os.getenv("ES_INDEX", "dataset_index")

OUT_DIR = "docs"
OUT_FILE = os.path.join(OUT_DIR, "index.html")

def connect():
    es = Elasticsearch(
        cloud_id=CLOUD_ID,
        basic_auth=(ES_USER, ES_PASS)
    )
    return es

def fetch_data(es, index):
    print("Consultando documentos de Elasticsearch...")
    resp = es.search(index=index, body={"query": {"match_all": {}}}, size=1000)
    hits = [h["_source"] for h in resp["hits"]["hits"]]
    df = pd.DataFrame(hits)
    return df

def make_plot(df):
    if "date" in df.columns and "value" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        fig = px.line(df, x="date", y="value", color="category",
                      title="Valores por fecha y categoría")
    else:
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1],
                         title="Gráfica simple")
    return fig

def save_html(fig):
    os.makedirs(OUT_DIR, exist_ok=True)
    fig.write_html(OUT_FILE)
    print("Gráfica guardada en:", OUT_FILE)

def main():
    es = connect()
    df = fetch_data(es, INDEX)
    fig = make_plot(df)
    save_html(fig)

if __name__ == "__main__":
    main()
