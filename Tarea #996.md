# Investigación sobre RAID

## ¿Qué es RAID?

RAID (Redundant Array of Independent/Inexpensive Disks) es una tecnología de almacenamiento que combina múltiples discos duros físicos en una sola unidad lógica con el objetivo de **mejorar el rendimiento, la redundancia o ambas**. Fue concebida en la década de 1980 por David A. Patterson, Garth Gibson y Randy Katz en la Universidad de California, Berkeley.

El principio de RAID es **distribuir o duplicar los datos entre varios discos** para aumentar la velocidad de acceso y/o proteger la información contra fallos de hardware.

---

## Objetivos principales de RAID

1. **Redundancia:** Proteger los datos mediante la duplicación o el uso de paridad para evitar pérdida de información en caso de fallas de disco.  
2. **Rendimiento:** Mejorar la velocidad de lectura/escritura mediante la distribución de datos entre varios discos.  
3. **Escalabilidad:** Permitir la adición de más discos para aumentar la capacidad y mejorar las prestaciones.  

---

## Niveles de RAID más comunes

### RAID 0 (Striping)
- **Descripción:** Divide los datos en bloques y los distribuye entre varios discos.  
- **Ventajas:** Mayor velocidad de lectura y escritura.  
- **Desventajas:** No ofrece redundancia; si un disco falla, se pierde toda la información.  
- **Uso típico:** Edición de video, procesamiento de grandes volúmenes de datos temporales.  

---

### RAID 1 (Mirroring)
- **Descripción:** Duplica los datos en dos discos idénticos.  
- **Ventajas:** Alta seguridad, ya que si un disco falla, los datos permanecen en el otro.  
- **Desventajas:** Se requiere el doble de capacidad, el rendimiento no siempre es superior.  
- **Uso típico:** Servidores que priorizan la disponibilidad de la información.  

---

### RAID 5 (Paridad distribuida)
- **Descripción:** Requiere al menos 3 discos. Los datos y la información de paridad se distribuyen entre todos los discos.  
- **Ventajas:** Balance entre rendimiento, capacidad y seguridad. Puede soportar la falla de un disco.  
- **Desventajas:** La reconstrucción tras un fallo es lenta y desgasta los discos restantes.  
- **Uso típico:** Servidores de archivos y bases de datos.  

---

### RAID 6 (Doble paridad)
- **Descripción:** Similar al RAID 5, pero con dos bloques de paridad.  
- **Ventajas:** Soporta la falla de hasta **dos discos** sin pérdida de datos.  
- **Desventajas:** Rendimiento de escritura más lento por el cálculo adicional de la paridad.  
- **Uso típico:** Almacenamiento de datos críticos que requieren alta seguridad.  

---

### RAID 10 (RAID 1+0)
- **Descripción:** Combinación de RAID 1 (mirroring) y RAID 0 (striping).  
- **Ventajas:** Alta velocidad y redundancia.  
- **Desventajas:** Coste elevado, ya que requiere un mínimo de 4 discos y la mitad se usa en espejado.  
- **Uso típico:** Servidores de alto rendimiento con necesidad de seguridad y velocidad.  

---

## Comparativa de niveles RAID

| Nivel | Mínimo de discos | Rendimiento | Redundancia | Capacidad útil |
|-------|------------------|-------------|-------------|----------------|
| RAID 0 | 2 | Alta | Ninguna | 100% |
| RAID 1 | 2 | Media | Alta | 50% |
| RAID 5 | 3 | Alta | Media | (N-1)/N |
| RAID 6 | 4 | Media | Muy alta | (N-2)/N |
| RAID 10 | 4 | Muy alta | Alta | 50% |

---

## Ventajas generales de RAID
- Mayor **seguridad de datos** (dependiendo del nivel).  
- Incremento de la **velocidad de lectura/escritura**.  
- Escalabilidad al agregar más discos.  

---

## Desventajas generales de RAID
- **Costo:** Requiere más discos.  
- **Complejidad:** Configuración y mantenimiento más complicados.  
- **Falsas expectativas:** RAID no reemplaza a las copias de seguridad, solo brinda redundancia.  

---

## Conclusiones

RAID es una herramienta fundamental en entornos de servidores y almacenamiento empresarial, ya que ofrece un balance entre **rendimiento, redundancia y capacidad**. Sin embargo, es importante elegir el nivel adecuado según las necesidades y recordar que **RAID no sustituye las copias de seguridad**, sino que complementa una estrategia de protección de datos.

---

## Referencias

- Patterson, D. A., Gibson, G., & Katz, R. H. (1988). *A Case for Redundant Arrays of Inexpensive Disks (RAID)*. ACM SIGMOD.  
- Tanenbaum, A. S., & Bos, H. (2015). *Modern Operating Systems*. Pearson.  
- Stallings, W. (2017). *Computer Organization and Architecture*. Pearson.  
