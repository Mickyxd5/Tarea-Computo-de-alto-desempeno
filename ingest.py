import os
import pandas as pd
from elasticsearch import Elasticsearch, helpers
from dateutil import parser

# Cargar las credenciales y configuración
CLOUD_ID = os.getenv("ES_CLOUD_ID")
ES_USER = os.getenv("ES_USER")
ES_PASS = os.getenv("ES_PASS")
INDEX = os.getenv("ES_INDEX", "dataset_index")

# Función de conexión a Elasticsearch Cloud
def connect():
    print("Conectando a Elasticsearch Cloud...")
    es = Elasticsearch(
        cloud_id=CLOUD_ID,
        basic_auth=(ES_USER, ES_PASS)
    )
    print("Conexión establecida:", es.info().body["cluster_name"])
    return es

# Normalizar los datos antes de enviarlos a Elasticsearch
def normalize_row(row):
    doc = row.dropna().to_dict()
    if "date" in doc:
        try:
            doc["date"] = parser.parse(str(doc["date"])).isoformat()
        except Exception:
            pass
    return doc

# Subir datos a Elasticsearch y verificar el estado
def main(csv_path="dataset/sample.csv"):
    # Cargar los datos desde el archivo CSV
    df = pd.read_csv(csv_path)
    print(f"Ingresando {len(df)} filas a {INDEX}...")

    # Conectar a Elasticsearch
    es = connect()

    # Verificar si el índice existe, sino crearlo
    if not es.indices.exists(index=INDEX):
        print(f"El índice '{INDEX}' no existe. Creando índice...")
        es.indices.create(index=INDEX, ignore=400)
    else:
        print(f"Índice '{INDEX}' ya existe.")

    # Preparar las acciones para cargar en Elasticsearch
    actions = [
        {"_index": INDEX, "_source": normalize_row(row)}
        for _, row in df.iterrows()
    ]

    # Subir los datos al índice de Elasticsearch
    try:
        helpers.bulk(es, actions)
        print("✅ Carga completa en Elasticsearch Cloud.")
    except Exception as e:
        print(f"❌ Error al cargar los datos: {e}")
        return

    # Verificación de la carga
    print(f"Verificando que los datos se subieron correctamente al índice '{INDEX}'...")
    verify_upload(es)

# Función para verificar si los datos se subieron correctamente
def verify_upload(es):
    try:
        response = es.search(
            index=INDEX,
            body={"query": {"match_all": {}}},
            size=5  # Recuperar los primeros 5 documentos
        )
        hits = response['hits']['hits']
        if hits:
            print(f"✅ Se subieron los siguientes {len(hits)} documentos al índice '{INDEX}':")
            for hit in hits:
                print(hit["_source"])
        else:
            print(f"❌ No se encontraron documentos en el índice '{INDEX}'.")
    except Exception as e:
        print(f"❌ Error al realizar la consulta de verificación: {e}")

# Ejecutar el script
if __name__ == "__main__":
    main()
