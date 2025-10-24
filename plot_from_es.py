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

df = pd.DataFrame(data)

# Ejemplo de gráfica
plt.figure(figsize=(8,4))
df["campo_x"].value_counts().plot(kind="bar")
plt.title("Gráfico desde Elasticsearch")

# Guardar en carpeta output
os.makedirs("output", exist_ok=True)
plt.savefig("output/grafica.png")
print("✅ Gráfica guardada en output/grafica.png")
