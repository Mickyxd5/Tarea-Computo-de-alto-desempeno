import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
import pandas as pd
import os

# Conexión a Elastic Cloud
es = Elasticsearch(
    cloud_id="TU_CLOUD_ID",
    basic_auth=("TU_USUARIO", "TU_PASSWORD")
)

# Consulta simple
resp = es.search(index="tudataset", body={"query": {"match_all": {}}}, size=1000)
data = [hit["_source"] for hit in resp["hits"]["hits"]]

# Convertir datos a DataFrame
df = pd.DataFrame(data)

# Verifica si 'campo_x' está en el DataFrame
if "campo_x" in df:
    print("✅ 'campo_x' encontrado en el DataFrame.")
    
    # Verifica que 'campo_x' no esté vacío
    if not df["campo_x"].isnull().all():
        # Generar la gráfica
        plt.figure(figsize=(8, 4))
        df["campo_x"].value_counts().plot(kind="bar")
        plt.title("Gráfico desde Elasticsearch")

        # Crear la carpeta output si no existe
        os.makedirs("output", exist_ok=True)

        # Guardar la gráfica en la carpeta output
        plt.savefig("output/grafica.png")
        print("✅ Gráfica guardada en output/grafica.png")
    else:
        print("⚠️ La columna 'campo_x' está vacía.")
else:
    print("⚠️ No se encontró 'campo_x' en el DataFrame.")
