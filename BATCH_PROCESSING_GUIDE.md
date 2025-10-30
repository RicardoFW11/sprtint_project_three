# 🚀 Batch Processing Guide

## ¿Qué es Batch Processing?

El batch processing procesa múltiples imágenes simultáneamente en lugar de una por una, mejorando significativamente el rendimiento del sistema.

## 📊 Beneficios Esperados

- **Throughput**: 2-3x más requests por segundo
- **Eficiencia**: Mejor uso de CPU/GPU
- **Costo**: Menor costo computacional por imagen

## 🔧 Cómo Usar

### Opción 1: Variable de Entorno

```bash
# Modo individual (default)
docker compose up -d

# Modo batch
docker compose down
export USE_BATCH_PROCESSING=true
docker compose up -d
```

### Opción 2: Modificar docker-compose.yml

Agregar la variable de entorno al servicio `model`:

```yaml
model:
  image: ml_service
  environment:
    - USE_BATCH_PROCESSING=true
    - BATCH_SIZE=4          # Opcional: tamaño del batch
    - BATCH_TIMEOUT=2.0     # Opcional: timeout en segundos
```

### Opción 3: Comando directo

```bash
# Dentro del contenedor
docker exec -it ml_service python3 /src/ml_service.py --batch
```

## ⚙️ Configuración

### Variables de Entorno

- **`USE_BATCH_PROCESSING`**: `true` para activar batch mode
- **`BATCH_SIZE`**: Número máximo de imágenes por batch (default: 4)
- **`BATCH_TIMEOUT`**: Tiempo máximo de espera para llenar un batch (default: 2.0s)

### Valores Recomendados

| Escenario | BATCH_SIZE | BATCH_TIMEOUT | Descripción |
|-----------|------------|---------------|-------------|
| Baja carga | 2 | 1.0 | Menor latencia |
| Carga media | 4 | 2.0 | Balance óptimo (default) |
| Alta carga | 8 | 3.0 | Máximo throughput |

## 🧪 Testing y Comparación

### 1. Test Individual (Baseline)

```bash
# Asegurar modo individual
docker compose down
docker compose up -d

# Ejecutar stress test
cd stress_test
locust -f locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2 --run-time 60s --headless
```

### 2. Test Batch

```bash
# Activar batch mode
docker compose down
export USE_BATCH_PROCESSING=true
docker compose up -d

# Verificar que está en modo batch
docker logs ml_service | grep "BATCH"
# Deberías ver: "BATCH PROCESSING MODE ENABLED"

# Ejecutar stress test
cd stress_test
locust -f locustfile.py --host=http://localhost:8000 --users 20 --spawn-rate 5 --run-time 60s --headless
```

### 3. Comparar Resultados

| Métrica | Individual | Batch | Mejora |
|---------|-----------|-------|--------|
| RPS (ML) | 1.2 | ? | ? |
| Latencia p50 | 104ms | ? | ? |
| Latencia p95 | 260ms | ? | ? |
| Errores | 0% | ? | ? |

## 📈 Monitoreo

### Ver logs en tiempo real

```bash
# Ver procesamiento batch
docker logs ml_service -f

# Buscar métricas de batch
docker logs ml_service | grep "Batch processed"
```

Ejemplo de output esperado:
```
Batch processed 4 jobs in 0.156s (0.039s per image)
Batch processed 3 jobs in 0.128s (0.043s per image)
```

### Verificar modo activo

```bash
docker logs ml_service | head -20
```

Deberías ver:
```
============================================================
BATCH PROCESSING MODE ENABLED
============================================================
Launching ML service with BATCH processing (size=4, timeout=2.0s)...
```

## 🎯 Troubleshooting

### Problema: Batch mode no se activa

**Solución**:
```bash
# Verificar variable de entorno
docker exec ml_service env | grep BATCH

# Reconstruir imagen
docker compose down
docker compose build model
docker compose up -d
```

### Problema: Latencia muy alta

**Solución**: Reducir `BATCH_TIMEOUT`
```bash
export BATCH_TIMEOUT=1.0
docker compose up -d
```

### Problema: Pocos requests por batch

**Solución**: Aumentar carga de usuarios en Locust
```bash
locust --users 30 --spawn-rate 10
```

## 📊 Análisis de Resultados

### Métricas Clave a Observar

1. **Throughput (RPS)**: Debería aumentar 2-3x
2. **Latencia individual**: Puede aumentar ligeramente
3. **Tamaño promedio de batch**: Idealmente cerca de BATCH_SIZE
4. **Tiempo por imagen**: Debería reducirse significativamente

### Cálculo de Eficiencia

```
Eficiencia = (Tiempo_Individual × Batch_Size) / Tiempo_Batch

Ejemplo:
Individual: 104ms por imagen
Batch de 4: 156ms total
Eficiencia = (104ms × 4) / 156ms = 2.67x
```

## 🚀 Próximos Pasos

1. Ejecutar test baseline (individual)
2. Activar batch processing
3. Ejecutar test batch con más usuarios
4. Comparar métricas
5. Ajustar BATCH_SIZE y BATCH_TIMEOUT según resultados
6. Documentar hallazgos en reporte

## 📝 Notas Importantes

- El batch processing es más efectivo con **alta carga concurrente**
- Con pocos usuarios, puede no ver mejoras significativas
- El modo batch **NO modifica** las funciones originales
- Ambos modos pueden coexistir en el código
- Los tests existentes **NO se ven afectados**

