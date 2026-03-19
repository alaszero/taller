# 📋 Solución: Migración de Datos en Sistema Multi-Taller

## Problema Detectado
Cuando creabas un nuevo taller en versión local, los datos históricos (materiales, herramientas, empleados, etc.) que ya existían en `rober_lang` no se asignaban automáticamente al nuevo taller, quedando éste completamente vacío.

## Causa Raíz
- ✅ Las columnas `taller_id` SÍ existen en todas las tablas (migración anterior)
- ✅ Todos los datos históricos SÍ están asignados a `rober_lang`
- ❌ El nuevo taller se creaba vacío (sin heredar datos)
- ❌ No había función que copiara datos maestros entre talleres

## Solución Implementada

### 1. **Nueva Función de Migración**
Se agregó `migrate_base_data_to_taller_raw()` en `data/sqlite_backend.py` que:

**Copia datos MAESTROS (compartidos entre talleres):**
- ✅ MATERIALES (catálogo de productos)
- ✅ HERRAMIENTAS (inventario de herramientas)
- ✅ EMPLEADOS (base de datos de personal)
- ✅ UBICACIONES (áreas del almacén)
- ✅ PROVEEDORES (contactos)
- ✅ ETAPAS (etapas de producción)

**NO copia datos TRANSACCIONALES (específicos por taller):**
- ❌ MOV_ALMACEN (movimientos de almacén)
- ❌ MOV_HERRA (préstamos de herramientas)
- ❌ PROYECTOS (obras en curso)
- ❌ MUEBLES, ORDENES_PRODUCCION, REG_AVANCE, LOTES

### 2. **Integración en API**
Se modificó el endpoint `POST /api/talleres` para:
1. Crear el nuevo taller en la tabla TALLERES
2. **Automáticamente** migrar datos base desde `rober_lang` (configurable)
3. El nuevo taller inicia con catálogos compartidos pero sin datos operacionales previos

## Cómo Funciona Ahora

### Escenario: Crear Nuevo Taller "Taller Oriente"

**Antes** (problema):
```
POST /api/talleres
{
  "id": "taller_oriente",
  "nombre": "Taller Oriente"
}
↓
Resultado: Taller vacío (0 materiales, 0 empleados, etc.)
```

**Después** (solucionado):
```
POST /api/talleres
{
  "id": "taller_oriente",
  "nombre": "Taller Oriente",
  "source_taller_id": "rober_lang"  // Opcional, por defecto usa rober_lang
}
↓
Resultado: Taller con 55 materiales, 10 herramientas, 8 empleados, 6 ubicaciones, 4 proveedores
```

## Verificación

Se probó la migración directamente:
```
Taller origen:   rober_lang
Taller destino:  testing2

Resultados:
✅ MATERIALES:      55 registros copiados
✅ HERRAMIENTAS:    10 registros copiados
✅ EMPLEADOS:        8 registros copiados
✅ UBICACIONES:      6 registros copiados
✅ PROVEEDORES:      4 registros copiados
✅ ETAPAS:           0 registros

TOTAL: 83 registros maestros copiados exitosamente
```

## Comportamiento Multi-Tenant Ahora

| Aspecto | Antes | Después |
|---------|-------|---------|
| Nuevo taller inicia | Vacío | Con catálogos base |
| Materiales compartidos | ❌ Cada taller copia | ✅ Heredados automáticamente |
| Movimientos aislados | ✅ Independientes | ✅ Independientes |
| Proyectos por taller | ✅ Independientes | ✅ Independientes |

## Instrucciones para Usuario

### Crear un Nuevo Taller:
1. Ve a **Administración → Talleres**
2. Haz clic en "Nuevo Taller"
3. Completa:
   - **ID**: `id_unico` (sin espacios, ej: `taller_centro`)
   - **Nombre**: Nombre visible (ej: "Taller Centro")
4. El sistema **automáticamente**:
   - ✅ Crea el taller
   - ✅ Copia materiales, herramientas, empleados, ubicaciones, proveedores
   - ✅ Inicia con datos maestros frescos

### Cambiar de Taller:
1. En el sidebar, selector "Taller activo"
2. Selecciona el taller deseado
3. Los datos se filtran automáticamente por taller

## Notas Técnicas

### Para Desarrolladores
- Función raw: `migrate_base_data_to_taller_raw(db_path, source, target)`
- Función Flask: `migrate_base_data_to_taller(source, target)`
- Se usa `INSERT OR IGNORE` para evitar duplicados por PK
- No duplica movimientos/proyectos (solo maestros)

### Base de Datos
```sql
-- Las tablas soportan multi-tenant:
CREATE TABLE MATERIALES (..., taller_id TEXT);
CREATE TABLE HERRAMIENTAS (..., taller_id TEXT);
-- ... etc

-- Índices optimizados:
CREATE INDEX idx_materiales_taller ON MATERIALES(taller_id);
```

## Estado Actual
- ✅ Feature implementado
- ✅ Probado en BD local
- ✅ Commit realizado: `4f42cf0`
- ✅ BD limpiada (solo `rober_lang`)
- 🔄 Listo para crear nuevos talleres con datos automáticos

## Próximas Mejoras (Opcional)
1. **Sincronización manual**: Endpoint para re-sincronizar datos base de un taller a otro
2. **UI mejorada**: Mostrar en formulario de nuevo taller de cuál copiar datos
3. **Auditoría**: Registrar qué datos se copiaron y de dónde
4. **Gestión de diferencias**: Detectar si dos talleres tienen catálogos diferentes
