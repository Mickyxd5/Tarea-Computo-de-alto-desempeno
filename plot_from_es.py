import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
import pandas as pd
import os

# Conexión a Elastic Cloud
es = Elasticsearch(
    cloud_id="TU_CLOUD_ID",  # Sustituye con tu Cloud ID
    basic_auth=("TU_USUARIO", "TU_PASSWORD")  # Sustituye con tus credenciales
)

# Consulta simple para obtener datos del índice
resp = es.search(index="tudataset", body={"query": {"match_all": {}}}, size=1000)

# Extraer los datos de la respuesta y convertir en DataFrame
data = [hit["_source"] for hit in resp["hits"]["hits"]]
df = pd.DataFrame(data)

# Verifica las primeras filas del DataFrame para asegurarte de que las columnas sean correctas
print(df.head())

# Suponiendo que 'home_goals' es una de las columnas en tu dataset
# Ejemplo de gráfico de goles locales vs goles visitantes
plt.figure(figsize=(10,6))
df[['home_goals', 'away_goals']].plot(kind='bar', stacked=True)
plt.title("Goles Locales vs Goles Visitantes")
plt.xlabel("Partidos")
plt.ylabel("Goles")
plt.legend(["Goles Locales", "Goles Visitantes"])

# Guardar la gráfica en la carpeta output
os.makedirs("output", exist_ok=True)
plt.savefig("output/grafica_goles.png")
plt.close()  # Cierra la figura para liberar memoria
print("✅ Gráfica guardada en output/grafica_goles.png")
