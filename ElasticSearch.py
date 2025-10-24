import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import numpy as np

# Intentar importar elasticsearch, pero continuar si no está disponible
try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    print("⚠️  Elasticsearch no está disponible. Continuando solo con visualizaciones...")

def main():
    print("Iniciando proceso de carga y visualización...")
    
    # 1. Cargar datos desde CSV y limpiar NaN
    try:
        df = pd.read_csv('data.csv')
        print(f"✅ Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
        
        # LIMPIAR DATOS: Reemplazar NaN por None (que Elasticsearch entiende)
        df_clean = df.replace({np.nan: None})
        print("✅ Datos limpiados (NaN → None)")
        
    except Exception as e:
        print(f"❌ Error cargando data.csv: {e}")
        return
    
    # 2. Conexión a Elasticsearch (solo si está disponible)
    if ELASTICSEARCH_AVAILABLE:
        es = connect_elasticsearch()
        if es:
            load_to_elasticsearch(es, df_clean)  # Usar datos limpios
        else:
            print("ℹ️  Continuando sin Elasticsearch")
    else:
        print("ℹ️  Elasticsearch no disponible - generando solo visualizaciones")
    
    # 3. Generar visualizaciones (usar datos originales para gráficos)
    generate_charts(df)
    
    # 4. Generar página HTML
    generate_html()
    
    print("🎉 Proceso completado exitosamente!")

def connect_elasticsearch():
    """Conectar a Elasticsearch usando variables de entorno"""
    try:
        es_cloud_id = os.getenv('ELASTIC_CLOUD_ID')
        es_username = os.getenv('ELASTIC_USERNAME')
        es_password = os.getenv('ELASTIC_PASSWORD')
        
        if es_cloud_id and es_username and es_password:
            # CORRECCIÓN: Usar basic_auth en lugar de http_auth
            es = Elasticsearch(
                cloud_id=es_cloud_id,
                basic_auth=(es_username, es_password)  # ← CAMBIADO AQUÍ
            )
        else:
            print("📝 Variables de Elasticsearch no configuradas")
            return None
        
        if es.ping():
            print("✅ Conectado a Elasticsearch")
            return es
        else:
            print("❌ No se pudo conectar a Elasticsearch")
            return None
            
    except Exception as e:
        print(f"❌ Error conectando a Elasticsearch: {e}")
        return None

def load_to_elasticsearch(es, df):
    """Cargar datos a Elasticsearch"""
    try:
        index_name = "dataset_portafolio"
        
        # Crear índice si no existe
        if not es.indices.exists(index=index_name):
            # Mapeo que permite null values
            mapping = {
                "mappings": {
                    "properties": {
                        "home_goals_extra_time": {"type": "float", "null_value": 0.0},
                        "away_goals_extratime": {"type": "float", "null_value": 0.0},
                        "home_goals_penalty": {"type": "keyword", "null_value": "none"}
                    }
                }
            }
            es.indices.create(index=index_name, body=mapping)
            print(f"✅ Índice creado: {index_name}")
        
        # Convertir DataFrame a documentos
        records = df.to_dict('records')
        
        # Indexar documentos con manejo de errores
        success_count = 0
        error_count = 0
        
        for i, record in enumerate(records):
            try:
                es.index(index=index_name, id=i+1, body=record)
                success_count += 1
            except Exception as e:
                print(f"⚠️  Error indexando documento {i+1}: {e}")
                error_count += 1
                continue
        
        print(f"✅ Datos cargados en Elasticsearch: {success_count} exitosos, {error_count} errores")
        
    except Exception as e:
        print(f"❌ Error cargando datos a Elasticsearch: {e}")

def generate_charts(df):
    """Generar gráficos y guardarlos en la carpeta docs"""
    
    # Configurar estilo
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Crear carpeta docs si no existe
    os.makedirs('docs', exist_ok=True)
    
    print("📈 Generando gráficos...")
    
    try:
        # GRÁFICO 1: Distribución de goles
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        df['home_goals'].hist(bins=20, alpha=0.7, color='blue', label='Local')
        df['away_goals'].hist(bins=20, alpha=0.7, color='red', label='Visitante')
        plt.title('Distribución de Goles')
        plt.xlabel('Goles')
        plt.ylabel('Frecuencia')
        plt.legend()
        
        plt.subplot(1, 2, 2)
        df['home_goals_fulltime'].hist(bins=20, alpha=0.7, color='green', label='Full Time')
        plt.title('Goles en Tiempo Completo (Local)')
        plt.xlabel('Goles')
        plt.ylabel('Frecuencia')
        
        plt.tight_layout()
        plt.savefig('docs/distribucion_goles.png', dpi=100, bbox_inches='tight')
        plt.close()
        print("✅ Gráfico de distribución de goles generado")
        
        # GRÁFICO 2: Resultados por temporada
        plt.figure(figsize=(10, 6))
        season_results = df.groupby('season').agg({
            'home_win': 'sum',
            'away_win': 'sum'
        }).reset_index()
        
        bar_width = 0.35
        x = range(len(season_results))
        
        plt.bar(x, season_results['home_win'], width=bar_width, label='Victorias Local', alpha=0.7)
        plt.bar([i + bar_width for i in x], season_results['away_win'], width=bar_width, label='Victorias Visitante', alpha=0.7)
        
        plt.xlabel('Temporada')
        plt.ylabel('Número de Victorias')
        plt.title('Victorias por Temporada')
        plt.xticks([i + bar_width/2 for i in x], season_results['season'])
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('docs/victorias_temporada.png', dpi=100, bbox_inches='tight')
        plt.close()
        print("✅ Gráfico de victorias por temporada generado")
        
        # GRÁFICO 3: Top equipos con más victorias
        home_wins = df[df['home_win'] == True]['home_team'].value_counts().head(10)
        away_wins = df[df['away_win'] == True]['away_team'].value_counts().head(10)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        home_wins.plot(kind='bar', ax=ax1, color='lightblue')
        ax1.set_title('Top 10 Equipos - Victorias como Local')
        ax1.set_xlabel('Equipo')
        ax1.set_ylabel('Victorias')
        ax1.tick_params(axis='x', rotation=45)
        
        away_wins.plot(kind='bar', ax=ax2, color='lightcoral')
        ax2.set_title('Top 10 Equipos - Victorias como Visitante')
        ax2.set_xlabel('Equipo')
        ax2.set_ylabel('Victorias')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('docs/top_equipos.png', dpi=100, bbox_inches='tight')
        plt.close()
        print("✅ Gráfico de top equipos generado")
        
        # GRÁFICO 4: Promedio de goles por temporada
        plt.figure(figsize=(10, 6))
        goals_by_season = df.groupby('season').agg({
            'home_goals': 'mean',
            'away_goals': 'mean'
        }).reset_index()
        
        plt.plot(goals_by_season['season'], goals_by_season['home_goals'], 
                marker='o', linewidth=2, label='Promedio Goles Local')
        plt.plot(goals_by_season['season'], goals_by_season['away_goals'], 
                marker='s', linewidth=2, label='Promedio Goles Visitante')
        
        plt.xlabel('Temporada')
        plt.ylabel('Promedio de Goles')
        plt.title('Evolución del Promedio de Goles por Temporada')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('docs/evolucion_goles.png', dpi=100, bbox_inches='tight')
        plt.close()
        print("✅ Gráfico de evolución de goles generado")
            
    except Exception as e:
        print(f"❌ Error generando gráficos: {e}")

def generate_html():
    """Generar página HTML principal"""
    
    # Listar archivos de gráficos generados
    image_files = [f for f in os.listdir('docs') if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Análisis de Partidos de Fútbol - Portafolio</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .header {{
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                border-left: 4px solid #667eea;
            }}
            .chart-container {{
                background: #f8f9fa;
                padding: 25px;
                margin: 25px 0;
                border-radius: 10px;
                border: 1px solid #e9ecef;
            }}
            .chart-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                gap: 30px;
            }}
            .chart-item {{
                text-align: center;
                padding: 20px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .chart-item:hover {{
                transform: translateY(-5px);
            }}
            .chart-item img {{
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }}
            .last-update {{
                text-align: center;
                color: #6c757d;
                font-style: italic;
                margin-top: 40px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
            }}
            h3 {{
                color: #495057;
                margin-bottom: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚽ Análisis de Partidos de Fútbol</h1>
                <p>Dashboard interactivo generado automáticamente con Python y GitHub Actions</p>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>📊 Gráficos</h3>
                        <p style="font-size: 24px; margin: 0; color: #667eea;">{len(image_files)}</p>
                    </div>
                    <div class="stat-card">
                        <h3>🔄 Actualizado</h3>
                        <p style="font-size: 16px; margin: 0; color: #28a745;">{pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>📈 Análisis Visual de los Partidos</h2>
                <div class="chart-grid">
    """
    
    # Agregar imágenes de gráficos
    for img_file in image_files:
        chart_name = img_file.replace('.png', '').replace('_', ' ').title()
        html_content += f"""
                    <div class="chart-item">
                        <h3>{chart_name}</h3>
                        <img src="{img_file}" alt="{chart_name}">
                    </div>
        """
    
    html_content += f"""
                </div>
            </div>
            
            <div class="last-update">
                <p>🚀 Generado automáticamente con GitHub Actions | ⚡ Análisis en tiempo real</p>
                <p>📅 Última actualización: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Página HTML generada: docs/index.html con {len(image_files)} gráficos")

if __name__ == "__main__":
    main()