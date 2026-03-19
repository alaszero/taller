"""
generar_manual.py — Genera el Manual de Usuario del Sistema de Taller
Ejecutar: python generar_manual.py
Salida:   manual_usuario.html  (ábrelo en cualquier navegador)
También importable desde Flask: from generar_manual import build_html
"""
import os
from datetime import datetime

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual_usuario.html")

def _read_version():
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")) as f:
            return f.read().strip()
    except Exception:
        return "2.0.0"

STYLE = """
:root{--primary:#1F4E79;--accent:#d4a017;--bg:#f4f6f9;--text:#2c3e50;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:Arial,'Helvetica Neue',sans-serif;font-size:10pt;background:#fff;color:var(--text);line-height:1.55;}
a{color:var(--primary);text-decoration:none;}
/* ── Layout ── */
.wrapper{display:flex;min-height:100vh;}
.toc{width:240px;flex-shrink:0;background:var(--primary);color:#c8d6e5;position:sticky;top:0;height:100vh;overflow-y:auto;padding:20px 0;}
.toc-title{font-size:13pt;font-weight:700;color:#fff;padding:0 18px 14px;border-bottom:1px solid rgba(255,255,255,.15);margin-bottom:8px;}
.toc a{display:block;padding:5px 18px;font-size:9pt;color:#c8d6e5;transition:background .15s;}
.toc a:hover{background:rgba(255,255,255,.1);color:#fff;}
.toc a.h2{font-weight:600;color:#fff;font-size:9.5pt;margin-top:6px;}
.toc a.h3{padding-left:30px;font-size:8.5pt;}
.content{flex:1;padding:40px 52px;max-width:900px;}
/* ── Headings ── */
h1{font-size:22pt;color:var(--primary);border-bottom:3px solid var(--accent);padding-bottom:8px;margin-bottom:20px;}
h2{font-size:15pt;color:var(--primary);margin:36px 0 10px;padding-left:10px;border-left:4px solid var(--accent);}
h3{font-size:11.5pt;color:#2e6da4;margin:22px 0 7px;}
h4{font-size:10pt;font-weight:700;margin:14px 0 5px;}
p{margin-bottom:9px;}
ul,ol{margin:6px 0 10px 22px;}
li{margin-bottom:4px;}
/* ── Elementos especiales ── */
.tip{background:#e8f4e8;border-left:4px solid #28a745;padding:8px 12px;border-radius:4px;margin:10px 0;font-size:9.5pt;}
.warning{background:#fff3cd;border-left:4px solid #ffc107;padding:8px 12px;border-radius:4px;margin:10px 0;font-size:9.5pt;}
.danger{background:#f8d7da;border-left:4px solid #dc3545;padding:8px 12px;border-radius:4px;margin:10px 0;font-size:9.5pt;}
table{width:100%;border-collapse:collapse;margin:10px 0 16px;font-size:9.5pt;}
th{background:var(--primary);color:#fff;padding:6px 10px;text-align:left;}
td{border:1px solid #dee2e6;padding:5px 10px;vertical-align:top;}
tr:nth-child(even) td{background:#f8f9fa;}
code{background:#eef2f7;padding:1px 5px;border-radius:3px;font-family:monospace;font-size:9pt;color:var(--primary);}
pre{background:#1e2329;color:#c9d1d9;padding:12px 16px;border-radius:6px;font-size:9pt;overflow-x:auto;margin:10px 0;}
.badge{display:inline-block;padding:1px 8px;border-radius:12px;font-size:8.5pt;font-weight:600;}
.badge-green{background:#d4edda;color:#155724;}
.badge-yellow{background:#fff3cd;color:#856404;}
.badge-blue{background:#cce5ff;color:#004085;}
.badge-red{background:#f8d7da;color:#721c24;}
.badge-gray{background:#e2e3e5;color:#383d41;}
.step{counter-increment:step;display:flex;gap:12px;margin-bottom:12px;}
.step-num{flex-shrink:0;width:26px;height:26px;background:var(--primary);color:#fff;border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:10pt;font-weight:700;margin-top:1px;}
.step-body{flex:1;}
.kbd{display:inline-block;background:#eee;border:1px solid #bbb;border-radius:3px;
  padding:1px 6px;font-family:monospace;font-size:8.5pt;}
.section-divider{border:none;border-top:2px solid #dee2e6;margin:40px 0;}
/* ── Cover ── */
.cover{text-align:center;padding:60px 0 40px;border-bottom:3px solid var(--accent);margin-bottom:40px;}
.cover h1{border:none;font-size:28pt;margin-bottom:8px;}
.cover .subtitle{font-size:13pt;color:#666;margin-bottom:4px;}
.cover .version{font-size:9pt;color:#999;}
@media print{.toc{display:none;}.content{max-width:100%;padding:20px;}h2{page-break-before:always;}}
"""

def sec(id_, text):
    return f'<h2 id="{id_}">{text}</h2>'

def sub(id_, text):
    return f'<h3 id="{id_}">{text}</h3>'

def tip(text):
    return f'<div class="tip">💡 {text}</div>'

def warn(text):
    return f'<div class="warning">⚠️ {text}</div>'

def danger(text):
    return f'<div class="danger">🔴 {text}</div>'

def badge(text, color="blue"):
    return f'<span class="badge badge-{color}">{text}</span>'

def kbd(k):
    return f'<span class="kbd">{k}</span>'

def step(n, title, body):
    return f'''<div class="step"><div class="step-num">{n}</div>
<div class="step-body"><strong>{title}</strong><br>{body}</div></div>'''

CONTENT = f"""
<div class="cover">
  <h1>Manual de Usuario</h1>
  <div class="subtitle">Sistema de Gestión de Taller de Carpintería</div>
  <div class="subtitle" style="margin-top:8px;">By <strong>Barrón</strong></div>
  <div class="version">Versión {_read_version()} &nbsp;·&nbsp; Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
</div>

<!-- ══════════════════════════════ INTRODUCCIÓN ══════════════════════════════ -->
{sec('intro', '1. Introducción')}
<p>El <strong>Sistema de Gestión de Taller</strong> es una aplicación web diseñada para administrar de forma
integral un taller de carpintería. Permite controlar el inventario de materiales y herramientas,
dar seguimiento a proyectos y órdenes de producción, y registrar el avance diario de los trabajadores.</p>

<h4>Tecnología</h4>
<ul>
  <li>Backend: <strong>Python + Flask</strong></li>
  <li>Base de datos: <strong>Archivos Excel (.xlsx)</strong> — no se requiere servidor de base de datos</li>
  <li>Interfaz: navegador web (Chrome, Edge, Firefox)</li>
</ul>

{sub('requisitos', '1.1 Requisitos para ejecutar')}
<table>
  <tr><th>Componente</th><th>Versión mínima</th><th>Notas</th></tr>
  <tr><td>Python</td><td>3.9+</td><td>Con pip</td></tr>
  <tr><td>Flask</td><td>2.x</td><td><code>pip install flask</code></td></tr>
  <tr><td>pandas</td><td>1.5+</td><td><code>pip install pandas openpyxl</code></td></tr>
  <tr><td>Navegador</td><td>Moderno</td><td>Chrome, Edge o Firefox recomendados</td></tr>
</table>

{sub('inicio', '1.2 Cómo iniciar el sistema')}
<div class="step"><div class="step-num">1</div>
<div class="step-body"><strong>Abrir una terminal</strong> en la carpeta <code>D:\\Proyectos</code></div></div>
<div class="step"><div class="step-num">2</div>
<div class="step-body"><strong>Ejecutar el servidor:</strong><pre>python app.py</pre></div></div>
<div class="step"><div class="step-num">3</div>
<div class="step-body"><strong>Abrir el navegador</strong> en <code>http://localhost:5000</code></div></div>
<div class="step"><div class="step-num">4</div>
<div class="step-body"><strong>Ingresar usuario y contraseña</strong> cuando el navegador lo solicite.<br>
Por defecto: usuario <code>admin</code> · contraseña <code>taller2024</code>.<br>
Se pueden cambiar con variables de entorno antes de iniciar: <code>set TALLER_USER=miusuario</code> y <code>set TALLER_PASS=micontraseña</code>.</div></div>
{tip('El servidor escucha en todas las interfaces de red (<code>0.0.0.0:5000</code>), por lo que es accesible desde cualquier dispositivo en la misma red Wi-Fi o LAN. Ve a <strong>Administración → Configuración de Red</strong> para ver la dirección IP de acceso.')}

{sub('estructura', '1.3 Estructura de archivos')}
<pre>
D:\\Proyectos\\
├── app.py                    ← Servidor Flask (punto de entrada)
├── generar_manual.py         ← Genera este manual
├── static/
│   ├── css/style.css         ← Estilos personalizados
│   └── js/main.js            ← JavaScript compartido
├── templates/                ← Páginas HTML
│   ├── base.html             ← Plantilla base (sidebar, topbar)
│   ├── dashboard.html
│   ├── almacen.html
│   ├── herramientas.html
│   ├── proyectos.html
│   ├── avance.html
│   ├── avance_dashboard.html
│   ├── empleados.html
│   ├── implementacion.html
│   └── admin.html
├── CAT/                      ← Catálogos (datos maestros)
│   ├── Materiales.xlsx
│   ├── Herramientas.xlsx
│   ├── Empleados.xlsx
│   ├── Ubicaciones.xlsx
│   ├── Proveedores.xlsx
│   └── Proyectos.xlsx        ← También contiene Muebles, OPs, Etapas
└── REG/                      ← Registros transaccionales
    ├── RegistroMovMaterial.xlsx
    ├── RegistroMovHerramienta.xlsx
    ├── RegAvance.xlsx
    └── Lotes.xlsx
</pre>

<hr class="section-divider">

<!-- ══════════════════════════════ MÓDULOS ══════════════════════════════ -->
{sec('dashboard', '2. Dashboard')}
<p>Pantalla de inicio que muestra un resumen ejecutivo del estado del taller en tiempo real.</p>

{sub('kpis', '2.1 Indicadores (KPIs)')}
<table>
  <tr><th>Indicador</th><th>Descripción</th></tr>
  <tr><td>{badge('Alertas de Stock','red')}</td><td>Materiales con stock en cero o por debajo del mínimo</td></tr>
  <tr><td>{badge('Herramientas Prestadas','yellow')}</td><td>Herramientas actualmente fuera del almacén</td></tr>
  <tr><td>{badge('Proyectos Activos','blue')}</td><td>Proyectos con estado "En proceso"</td></tr>
  <tr><td>{badge('Registros Hoy','green')}</td><td>Registros de avance capturados en el día</td></tr>
</table>

{sub('dash-alertas', '2.2 Tabla de alertas de stock')}
<p>Muestra los materiales críticos ordenados por nivel de urgencia. El semáforo de colores indica:</p>
<ul>
  <li>{badge('Sin stock','red')} — Stock = 0 (requiere compra inmediata)</li>
  <li>{badge('Bajo mínimo','yellow')} — Stock menor al mínimo configurado</li>
  <li>{badge('OK','green')} — Stock suficiente</li>
</ul>

{sub('dash-progreso', '2.3 Progreso de obras')}
<p>Tarjetas de progreso por proyecto activo. El porcentaje representa OPs que tienen al menos
un registro de avance respecto al total de OPs del proyecto.</p>

<hr class="section-divider">

<!-- ══════════════════════════════ ALMACÉN ══════════════════════════════ -->
{sec('almacen', '3. Almacén')}
<p>Módulo central para el control de inventario. El stock se calcula automáticamente
a partir de todos los movimientos registrados: <code>Stock = Σ Entradas − Σ Salidas</code>.</p>

{sub('stock', '3.1 Stock Actual')}
<p>Tabla con el inventario en tiempo real de todos los materiales. Incluye:</p>
<ul>
  <li>Código, descripción, unidad, stock mínimo</li>
  <li>Stock actual con semáforo de colores</li>
  <li>Indicador de estado: Sin stock / Bajo mínimo / OK</li>
</ul>
{tip('El stock se calcula al vuelo desde los movimientos, no se almacena directamente. Esto garantiza consistencia.')}

{sub('movimientos', '3.2 Registrar Movimiento')}
<p>Para registrar un movimiento de almacén:</p>
{step(1,'Clic en "Nuevo movimiento"','Abre el modal de registro.')}
{step(2,'Selecciona el Tipo','<b>Entrada</b>: material que entra al almacén (compra, donación).<br><b>Salida</b>: material que sale para un proyecto.<br><b>Traslado</b>: cambio de ubicación dentro del almacén.')}
{step(3,'Busca el material','Escribe el nombre o código para filtrar con el autocomplete.')}
{step(4,'Ingresa la cantidad','Para unidades enteras (pza, pie) no se permiten decimales.<br>Para unidades continuas (kg, lt, m) sí se permiten.')}
{step(5,'Completa los demás campos','Proyecto, mueble, responsable, ubicación de origen/destino.')}
{step(6,'Guarda','El sistema registra el timestamp automáticamente (fecha y hora).')}
{warn('Para Salidas, el sistema valida que haya stock suficiente. Si la cantidad es mayor al stock disponible, el movimiento es rechazado.')}

{sub('catalogo-mat', '3.3 Catálogo de Materiales')}
<p>Permite agregar y editar materiales. Campos:</p>
<table>
  <tr><th>Campo</th><th>Descripción</th><th>Ejemplo</th></tr>
  <tr><td>Código</td><td>Identificador único</td><td>MAT001</td></tr>
  <tr><td>Tipo</td><td>Tablero, Madera, Herraje, Consumible, EPP</td><td>Tablero</td></tr>
  <tr><td>Descripción</td><td>Nombre completo del material</td><td>MDF 15mm</td></tr>
  <tr><td>Unidad</td><td>Unidad de medida</td><td>pza, pie, m, kg, lt</td></tr>
  <tr><td>Stock mínimo</td><td>Umbral de alerta</td><td>5</td></tr>
</table>

{sub('mapa-ubic', '3.4 Mapa de Ubicaciones')}
<p>Visualiza el inventario distribuido por zona del almacén. Tres vistas disponibles:</p>
<ul>
  <li><strong>Tarjetas</strong> — vista visual por zona/estante/nivel</li>
  <li><strong>Tabla</strong> — vista tabular para búsqueda rápida</li>
  <li><strong>Lista</strong> — vista compacta</li>
</ul>
<p>La tarjeta <strong>{badge('SIN UBICACIÓN','yellow')}</strong> muestra materiales en stock que no tienen
ubicación asignada. Para asignarles ubicación, registra un <em>Traslado</em> especificando la ubicación destino.</p>

<hr class="section-divider">

<!-- ══════════════════════════════ HERRAMIENTAS ══════════════════════════════ -->
{sec('herramientas', '4. Herramientas')}
<p>Módulo para gestionar el préstamo y control de herramientas del taller.</p>

{sub('prestamo', '4.1 Registrar Préstamo')}
{step(1,'Clic en "Registrar préstamo"','El sistema auto-genera el folio (PREST001, PREST002…)')}
{step(2,'Selecciona la herramienta','Solo aparecen las herramientas disponibles (no prestadas).')}
{step(3,'Selecciona el responsable y proyecto','El responsable es quien se lleva la herramienta.')}
{step(4,'Clic en Registrar','El sistema guarda el préstamo y abre automáticamente un <strong>comprobante imprimible</strong> con dos copias: una para el trabajador y otra para el almacén.')}

{sub('devolucion', '4.2 Registrar Devolución')}
<p>En la pestaña "Préstamos activos", clic en <strong>Devolver</strong>. El sistema registra la fecha
de devolución automáticamente.</p>

{sub('cat-herr', '4.3 Catálogo e Inventario')}
<p>La pestaña "Catálogo" muestra todas las herramientas. El botón
<strong>Imprimir inventario</strong> genera una hoja física con todas las herramientas,
su estado actual en el sistema, y columnas vacías para verificación física y observaciones.</p>

<hr class="section-divider">

<!-- ══════════════════════════════ PROYECTOS ══════════════════════════════ -->
{sec('proyectos', '5. Proyectos')}
<p>Administra la estructura jerárquica: <strong>Proyecto → Mueble → Orden de Producción (OP)</strong>.</p>

{sub('jerarquia', '5.1 Jerarquía')}
<table>
  <tr><th>Nivel</th><th>Ejemplo</th><th>Descripción</th></tr>
  <tr><td>Proyecto</td><td>Casa Rancho (PROY001)</td><td>Obra o cliente para quien se trabaja</td></tr>
  <tr><td>Mueble</td><td>Closet Principal (MUE005)</td><td>Pieza de mobiliario dentro del proyecto</td></tr>
  <tr><td>OP</td><td>Corte (OP023)</td><td>Etapa de trabajo de un mueble</td></tr>
</table>

{sub('muebles', '5.2 Muebles')}
<p>Cada mueble pertenece a un proyecto. Campos del formulario:</p>
<table>
  <tr><th>Campo</th><th>Descripción</th></tr>
  <tr><td>ID Mueble</td><td>Auto-generado (MUE001, MUE002…)</td></tr>
  <tr><td>Nombre</td><td>Descripción del mueble</td></tr>
  <tr><td>Proyecto</td><td>Obra a la que pertenece</td></tr>
  <tr><td>Tipo</td><td>Closet, Cocina, Puerta, etc.</td></tr>
  <tr><td>Cantidad</td><td>Piezas iguales del mismo mueble</td></tr>
  <tr><td>Prioridad</td><td>{badge('Normal','gray')} · {badge('Media','yellow')} · {badge('Alta','red')} — nivel de urgencia de fabricación</td></tr>
</table>

{sub('ops', '5.3 Órdenes de Producción (OPs)')}
<p>Una OP representa una etapa de trabajo para un mueble específico.</p>

<h4>Crear una nueva OP</h4>
{step(1,'Selecciona la Obra','El selector de mueble se filtra automáticamente para mostrar solo los muebles del proyecto elegido.')}
{step(2,'Selecciona el Mueble','Solo aparecen los muebles que pertenecen a la obra seleccionada.')}
{step(3,'ID OP','Se genera automáticamente (OP001, OP002…). No es necesario escribirlo.')}
{step(4,'Completa el resto','Etapa, fechas, responsable y observaciones.')}
{step(5,'Guarda','La OP queda registrada y aparece en la tabla.')}

<h4>Tabla de OPs</h4>
<p>La tabla incluye una columna <strong>Proyecto</strong> para identificar rápidamente a qué obra pertenece cada OP.
Un selector de filtro por obra en la parte superior permite ver solo las OPs de un proyecto específico.</p>

<h4>Imprimir una OP</h4>
<p>Cada fila de la tabla tiene un botón <strong>Imprimir</strong> que genera un documento A4 con:</p>
<ul>
  <li>Encabezado con datos de la OP, proyecto, mueble y fechas</li>
  <li>Tabla de datos completa</li>
  <li>Cuadro de instrucciones</li>
  <li>Tres firmas: Encargado, Carpintero, Laqueado</li>
  <li>Pie de página <em>BY BARRÓN · SISTEMA DE GESTIÓN DE TALLER</em></li>
</ul>
{tip('El documento imprimible reserva espacio en la parte superior para el membrete preimpreso del taller.')}

{sub('etapas', '5.4 Etapas de producción')}
<p>Orden estándar de etapas:</p>
<ol>
  <li>Corte</li>
  <li>Maquinado</li>
  <li>Armado</li>
  <li>Masillado</li>
  <li>Lijado</li>
  <li>Sellado</li>
  <li>Laqueado base</li>
  <li>Lijado fino</li>
  <li>Laqueado final</li>
  <li>Instalación</li>
</ol>
{tip('Puedes editar proyectos, muebles y OPs haciendo clic en el ícono ✏ de cada fila.')}

<hr class="section-divider">

<!-- ══════════════════════════════ AVANCE ══════════════════════════════ -->
{sec('avance', '6. Avance de Obras')}
<p>Módulo para registrar y visualizar el progreso de producción diario.</p>

{sub('registrar-av', '6.1 Registrar Avance')}
{step(1,'Selecciona la Obra (proyecto)','Filtra automáticamente los muebles disponibles.')}
{step(2,'Selecciona el Mueble','Filtra las OPs de ese mueble.')}
{step(3,'Selecciona la OP','Elige la orden de producción que se trabajó.')}
{step(4,'Completa el registro','Empleado, etapa, estado, horas y piezas completadas.')}
{step(5,'Guarda','El registro queda guardado con la fecha actual.')}

{sub('vistas-av', '6.2 Vistas')}
<table>
  <tr><th>Vista</th><th>Descripción</th></tr>
  <tr><td>Lista</td><td>Tabla de todos los registros de avance con filtros</td></tr>
  <tr><td>Por obra</td><td>Cards por proyecto con OPs agrupadas por mueble y % de avance</td></tr>
  <tr><td>Por mueble</td><td>Cards individuales por mueble con sus OPs y % de avance</td></tr>
</table>

{sub('filtros-av', '6.3 Filtros')}
<p>Los filtros están en cascada: <strong>Obra → OP → Estado → Empleado</strong>.
Al limpiar el filtro de Obra se muestran todas las obras.</p>

{sub('imprimir-av', '6.4 Hoja de Registro Imprimible')}
<p>El botón <strong>Imprimir hoja</strong> genera un documento físico con todas las OPs activas
(no completadas), agrupadas por obra y mueble, con columnas en blanco para que los trabajadores
lo llenen durante el día y se capture en el sistema al final del turno.</p>

{sub('dash-av', '6.5 Dashboard de Avance')}
<p>Accesible desde el botón <strong>Dashboard</strong>. Muestra un panorama completo del avance
por obra con gráficas, filtros y estadísticas por proyecto y mueble.</p>

<hr class="section-divider">

<!-- ══════════════════════════════ EMPLEADOS ══════════════════════════════ -->
{sec('empleados', '7. Empleados')}
<p>Catálogo de trabajadores activos. Los empleados se usan en registros de avance y préstamos de herramientas.</p>
<table>
  <tr><th>Campo</th><th>Descripción</th></tr>
  <tr><td>EmpleadoID</td><td>Código único (EMP001…)</td></tr>
  <tr><td>Nombre / Apellido</td><td>Nombre completo</td></tr>
  <tr><td>Alias</td><td>Nombre corto para identificación rápida</td></tr>
  <tr><td>Área</td><td>Carpintería, Lacado, Oficina</td></tr>
  <tr><td>Puesto</td><td>Carpintero, Laqueador, Supervisor</td></tr>
  <tr><td>Especialidad</td><td>Habilidad principal</td></tr>
</table>

<hr class="section-divider">

<!-- ══════════════════════════════ IMPLEMENTACIÓN ══════════════════════════════ -->
{sec('implementacion', '8. Implementación')}
<p>Sección con formularios imprimibles para levantar la información inicial del taller
y cargarla al sistema. Recomendada al iniciar el uso del sistema por primera vez.</p>

{sub('flujo-imp', '8.1 Flujo de implementación recomendado')}
<div class="step"><div class="step-num">1</div>
<div class="step-body"><strong>Catálogo de Materiales</strong> — Registra todos los materiales e insumos del taller.</div></div>
<div class="step"><div class="step-num">2</div>
<div class="step-body"><strong>Catálogo de Herramientas</strong> — Alta de todas las herramientas con su N/S y ubicación.</div></div>
<div class="step"><div class="step-num">3</div>
<div class="step-body"><strong>Empleados</strong> — Alta de trabajadores activos.</div></div>
<div class="step"><div class="step-num">4</div>
<div class="step-body"><strong>Proyectos y Muebles</strong> — Estructura de la obra actual.</div></div>
<div class="step"><div class="step-num">5</div>
<div class="step-body"><strong>Órdenes de Producción</strong> — Una OP por cada etapa de cada mueble.</div></div>
<div class="step"><div class="step-num">6</div>
<div class="step-body"><strong>Inventario Inicial</strong> — Conteo físico del almacén. Se carga como movimientos de <em>Entrada</em>.</div></div>
<div class="step"><div class="step-num">7</div>
<div class="step-body"><strong>Registro de Avance histórico</strong> (opcional) — Avances previos al sistema.</div></div>
{warn('Carga los datos en el orden indicado. Los proyectos deben existir antes de cargar muebles, y los muebles antes de las OPs.')}

{sub('forms-disponibles', '8.2 Formularios disponibles')}
<table>
  <tr><th>Formulario</th><th>Se carga en</th></tr>
  <tr><td>Catálogo de Materiales</td><td>Almacén → Catálogo de materiales</td></tr>
  <tr><td>Inventario Inicial</td><td>Almacén → Nuevo movimiento (Entrada)</td></tr>
  <tr><td>Catálogo de Herramientas</td><td>Herramientas → Catálogo → Agregar herramienta</td></tr>
  <tr><td>Empleados</td><td>Empleados → Agregar empleado</td></tr>
  <tr><td>Proyectos y Muebles</td><td>Proyectos → Nuevo proyecto / Nuevo mueble</td></tr>
  <tr><td>Órdenes de Producción</td><td>Proyectos → Nueva OP</td></tr>
  <tr><td>Registro de Avance</td><td>Avance → Registrar avance</td></tr>
  <tr><td>Movimientos de Almacén</td><td>Almacén → Nuevo movimiento</td></tr>
  <tr><td>Préstamo de Herramientas</td><td>Herramientas → Registrar préstamo</td></tr>
</table>

<hr class="section-divider">

<!-- ══════════════════════════════ ADMINISTRACIÓN ══════════════════════════════ -->
{sec('admin', '9. Administración')}
{danger('Esta sección contiene acciones irreversibles. Úsala solo si es absolutamente necesario.')}

{sub('reset', '9.1 Borrar datos')}
<p>Permite eliminar registros de forma granular:</p>
<ul>
  <li><strong>Registros transaccionales</strong>: movimientos, préstamos, avances, lotes. Útil al iniciar un nuevo período.</li>
  <li><strong>Catálogos</strong>: materiales, herramientas, empleados, proyectos, muebles, OPs.</li>
  <li><strong>Todo</strong>: deja el sistema completamente vacío como si fuera nuevo.</li>
</ul>
<p>Para confirmar cualquier borrado, debes escribir <code>BORRAR</code> en el campo de confirmación.</p>
{warn('Siempre haz un backup antes de borrar datos. La operación es irreversible.')}

{sub('backup', '9.2 Respaldo y Restauración')}
<p>La sección <strong>Respaldo del Sistema</strong> permite exportar todos los datos a un archivo
comprimido y restaurarlos en caso de pérdida o migración.</p>

<h4>Exportar backup</h4>
<p>El botón <strong>Descargar backup</strong> genera un archivo <code>.zip</code> que contiene
todos los archivos Excel del sistema, con la siguiente estructura:</p>
<table>
  <tr><th>Archivo en el ZIP</th><th>Contenido</th></tr>
  <tr><td><code>CAT/Materiales.xlsx</code></td><td>Catálogo de materiales e insumos</td></tr>
  <tr><td><code>CAT/Herramientas.xlsx</code></td><td>Catálogo de herramientas</td></tr>
  <tr><td><code>CAT/Empleados.xlsx</code></td><td>Catálogo de trabajadores</td></tr>
  <tr><td><code>CAT/Proyectos.xlsx</code></td><td>Proyectos, muebles, OPs y etapas</td></tr>
  <tr><td><code>CAT/Ubicaciones.xlsx</code></td><td>Ubicaciones del almacén</td></tr>
  <tr><td><code>CAT/Proveedores.xlsx</code></td><td>Catálogo de proveedores</td></tr>
  <tr><td><code>REG/RegistroMovMaterial.xlsx</code></td><td>Movimientos de almacén</td></tr>
  <tr><td><code>REG/RegistroMovHerramienta.xlsx</code></td><td>Préstamos de herramientas</td></tr>
  <tr><td><code>REG/RegAvance.xlsx</code></td><td>Registros de avance diario</td></tr>
  <tr><td><code>REG/Lotes.xlsx</code></td><td>Lotes de material comprado</td></tr>
</table>
<p>El archivo se descarga con nombre <code>backup_YYYY-MM-DD_HHMM.zip</code>.</p>
{tip('Programa backups periódicos (semanal o diario) y guárdalos en OneDrive, Google Drive o disco externo.')}

<h4>Restaurar backup</h4>
{step(1, 'Selecciona el archivo', 'Usa el selector de archivo para cargar un <code>.zip</code> exportado previamente desde este mismo sistema.')}
{step(2, 'Clic en Restaurar', 'El sistema muestra un diálogo de confirmación advirtiendo que los datos actuales serán sobreescritos.')}
{step(3, 'Confirma la operación', 'Los archivos Excel del sistema son reemplazados por los del backup. El sistema refleja los datos restaurados de inmediato.')}
{danger('La restauración sobreescribe los archivos actuales sin posibilidad de recuperación. Si tienes datos recientes que quieres conservar, haz un backup de la versión actual antes de restaurar una anterior.')}

{sub('editor-bd', '9.3 Editor de Base de Datos')}
<p>Permite ver y modificar directamente los registros de cualquier tabla del sistema, tal como están almacenados en Excel.</p>
{danger('Los cambios en el editor se aplican directamente al archivo Excel. Un dato incorrecto puede afectar el funcionamiento del sistema. Úsalo solo para correcciones puntuales.')}

<h4>Uso del editor</h4>
{step(1,'Selecciona la tabla','Elige una tabla del selector desplegable. Las tablas están agrupadas en <em>Catálogos</em> y <em>Registros</em>.')}
{step(2,'Edita una celda','Haz clic en cualquier celda para activar un campo de edición. Presiona <kbd>Enter</kbd> para confirmar o <kbd>Esc</kbd> para cancelar.')}
{step(3,'Celdas modificadas','Las celdas con cambios pendientes se resaltan en amarillo. El botón 💾 de la fila también cambia a amarillo.')}
{step(4,'Guarda la fila','Clic en 💾 para guardar todos los cambios de esa fila en el Excel.')}
{step(5,'Elimina una fila','Clic en el ícono de papelera y confirma. La eliminación es inmediata e irreversible.')}
{tip('Usa el campo de búsqueda para filtrar filas por cualquier valor. Es útil en tablas con muchos registros.')}

{sub('red', '9.4 Configuración de Red')}
<p>Panel de control de acceso al sistema desde distintos dispositivos y redes.</p>

<h4>Autenticación</h4>
<p>El interruptor <strong>Autenticación</strong> activa o desactiva la solicitud de usuario y contraseña al ingresar al sistema. El cambio tiene efecto inmediato, sin necesidad de reiniciar.</p>
<table>
  <tr><th>Estado</th><th>Cuándo usarlo</th></tr>
  <tr><td>{badge('Activada','green')}</td><td>Siempre que el sistema sea accesible desde internet o redes no controladas</td></tr>
  <tr><td>{badge('Desactivada','red')}</td><td>Solo en redes completamente privadas y de confianza, para facilitar el acceso</td></tr>
</table>
{warn('Si desactivas la autenticación y el sistema es accesible desde internet (por ejemplo, con el túnel activo), cualquier persona podrá ver y modificar los datos.')}

<h4>Modo de acceso — LAN</h4>
<p>El servidor siempre escucha en todas las interfaces de red. La sección muestra la <strong>IP de red local</strong> detectada automáticamente. Cualquier dispositivo en la misma red Wi-Fi o LAN puede acceder usando esa URL.</p>
{tip('Si el firewall de Windows bloquea el acceso, abre el puerto 5000 en las reglas de entrada de Windows Defender Firewall.')}

<h4>Túnel de Internet (Cloudflare)</h4>
<p>Permite acceder al sistema desde cualquier red o dispositivo fuera de la LAN, sin necesidad de abrir puertos en el router. Requiere tener instalado <strong>cloudflared</strong>.</p>
{step(1,'Instala cloudflared','Descárgalo desde <code>developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads</code>')}
{step(2,'Clic en "Iniciar túnel"','El sistema lanza cloudflared en segundo plano.')}
{step(3,'Espera la URL pública','En unos segundos aparece una URL del tipo <code>https://xxxx.trycloudflare.com</code>.')}
{step(4,'Comparte la URL','Cualquier persona con esa URL puede acceder al sistema (si la autenticación está activa, requerirá usuario y contraseña).')}
{step(5,'Detén el túnel','Cuando ya no necesites acceso externo, clic en "Detener" para cerrar el túnel.')}
{warn('La URL del túnel cambia cada vez que se inicia. No es permanente. Para URLs fijas se requiere una cuenta de Cloudflare.')}

<hr class="section-divider">

<!-- ══════════════════════════════ SERVIDOR Y PRODUCCIÓN ══════════════════════════════ -->
{sec('servidor', '10. Servidor y Producción')}
<p>El sistema funciona en dos entornos: <strong>local</strong> (tu PC Windows con archivos Excel) y
<strong>producción</strong> (servidor Ubuntu con SQLite, accesible desde <code>yekflow.com</code>).
Esta sección explica cómo actualizar la versión en producción y los comandos principales del servidor.</p>

{sub('flujo-deploy', '10.1 Flujo de actualización')}
<p>Cuando hagas cambios al sistema en tu PC local (Windows), sigue estos pasos para llevarlos a producción:</p>

{step(1, 'Modifica y prueba en local', 'Haz los cambios necesarios en el código. Ejecuta <code>python app.py</code> y prueba en <code>http://localhost:5000</code> hasta que todo funcione correctamente.')}
{step(2, 'Genera el paquete del servidor', 'Ve a <strong>Administración</strong> → sección <strong>Paquete del Servidor</strong> → clic en <strong>Generar y descargar ZIP</strong>. Se descargará un archivo como <code>taller_servidor_20260317_1430.zip</code>.')}
{step(3, 'Copia el ZIP al servidor', 'Copia el archivo ZIP a la carpeta <code>/home/serv-bar/Documentos/YekflowExports/</code> del servidor Ubuntu. Puedes usar una USB, carpeta compartida en red, o el comando SCP desde PowerShell:<br><pre>scp taller_servidor_20260317_1430.zip serv-bar@192.168.100.156:/home/serv-bar/Documentos/YekflowExports/</pre>')}
{step(4, 'Ejecuta la actualización en el servidor', 'Abre una terminal en Ubuntu y ejecuta:<pre>sudo actualizar-taller /home/serv-bar/Documentos/YekflowExports/taller_servidor_20260317_1430.zip</pre>El comando <code>actualizar-taller</code> funciona desde cualquier carpeta. No necesitas hacer <code>cd</code> a ningún lugar.')}
{step(5, 'Verifica', 'El script reinicia el servicio automáticamente. Abre <code>https://yekflow.com</code> en el navegador y confirma que los cambios están en vivo.')}

{tip('El ZIP <strong>no incluye la base de datos</strong> (<code>taller.db</code>). Los datos de producción en el servidor se mantienen intactos al actualizar.')}

<h4>Instalación del comando de actualización (solo la primera vez)</h4>
<p>El comando <code>actualizar-taller</code> debe instalarse una sola vez en el servidor. Si al ejecutarlo
te dice <em>"comando no encontrado"</em>, instálalo así:</p>
<pre># Primero extrae el instalador del ZIP:
cd /home/serv-bar/Documentos/YekflowExports
unzip -o taller_servidor_20260317_1430.zip instalar_actualizador.sh
sudo bash instalar_actualizador.sh</pre>
<p>Después de esto, el comando <code>sudo actualizar-taller</code> quedará disponible permanentemente.</p>

<h4>¿Qué hace el comando de actualización?</h4>
<ol>
  <li>Hace un backup automático de <code>taller.db</code> antes de cualquier cambio</li>
  <li>Extrae los archivos nuevos (templates, CSS, Python, etc.) sin tocar la base de datos</li>
  <li>Actualiza dependencias de Python si cambiaron</li>
  <li>Ajusta permisos de archivos</li>
  <li>Reinicia el servicio para que los cambios tomen efecto</li>
</ol>

{sub('comandos-servidor', '10.2 Comandos del servidor')}
<p>Referencia rápida de los comandos más usados en la terminal del servidor Ubuntu.</p>

<h4>Ver estado</h4>
<table>
  <tr><th>Comando</th><th>Descripción</th></tr>
  <tr><td><code>systemctl status taller</code></td><td>Ver si la app está corriendo</td></tr>
  <tr><td><code>systemctl status cloudflared</code></td><td>Ver si el túnel de Cloudflare está activo</td></tr>
</table>

<h4>Iniciar, detener y reiniciar</h4>
<table>
  <tr><th>Comando</th><th>Descripción</th></tr>
  <tr><td><code>sudo systemctl start taller</code></td><td>Iniciar la app</td></tr>
  <tr><td><code>sudo systemctl stop taller</code></td><td>Detener la app</td></tr>
  <tr><td><code>sudo systemctl restart taller</code></td><td>Reiniciar la app</td></tr>
  <tr><td><code>sudo systemctl restart taller cloudflared</code></td><td>Reiniciar app y túnel</td></tr>
</table>

<h4>Ver tráfico y logs en vivo</h4>
<table>
  <tr><th>Comando</th><th>Descripción</th></tr>
  <tr><td><code>journalctl -u taller -f</code></td><td>Ver tráfico de la app en tiempo real (Ctrl+C para salir)</td></tr>
  <tr><td><code>journalctl -u taller -n 50</code></td><td>Ver las últimas 50 líneas de log</td></tr>
  <tr><td><code>journalctl -u taller --since "10 min ago"</code></td><td>Logs de los últimos 10 minutos</td></tr>
  <tr><td><code>journalctl -u taller -p err -n 20</code></td><td>Ver solo errores recientes</td></tr>
  <tr><td><code>journalctl -u cloudflared -f</code></td><td>Tráfico del túnel en vivo</td></tr>
  <tr><td><code>journalctl -u taller -u cloudflared -f</code></td><td>App y túnel combinados en vivo</td></tr>
</table>
{tip('El comando <code>journalctl -u taller -f</code> es el más útil para monitorear quién está usando el sistema. Muestra cada solicitud HTTP con la hora, ruta y código de respuesta.')}

<h4>Red y conexiones</h4>
<table>
  <tr><th>Comando</th><th>Descripción</th></tr>
  <tr><td><code>hostname -I</code></td><td>Ver la IP del servidor</td></tr>
  <tr><td><code>ss -tnp | grep :5000</code></td><td>Conexiones activas a la app</td></tr>
  <tr><td><code>curl -s http://localhost:5000</code></td><td>Verificar que la app responde</td></tr>
</table>

<h4>Encender y apagar el servidor</h4>
<table>
  <tr><th>Comando</th><th>Descripción</th></tr>
  <tr><td><code>sudo shutdown now</code></td><td>Apagar el servidor inmediatamente</td></tr>
  <tr><td><code>sudo shutdown +5 "mensaje"</code></td><td>Apagar en 5 minutos con aviso</td></tr>
</table>
{tip('Al encender la PC Ubuntu, los servicios <code>taller</code> y <code>cloudflared</code> se inician automáticamente. No es necesario hacer nada manualmente.')}

<h4>Backup manual de la base de datos</h4>
<pre>sudo cp /home/taller/app/taller.db /home/taller/backups/taller_manual_$(date +%Y%m%d_%H%M%S).db</pre>

{sub('diferencias', '10.3 Diferencias entre versión local y producción')}
<p>El sistema tiene dos versiones del backend que comparten la misma interfaz (templates y CSS) pero difieren en cómo almacenan los datos y gestionan los usuarios:</p>

<table>
  <tr><th>Característica</th><th>Local (desarrollo)</th><th>Producción (servidor)</th></tr>
  <tr><td>Archivo principal</td><td><code>app.py</code></td><td><code>app_web.py</code></td></tr>
  <tr><td>Base de datos</td><td>Archivos Excel (<code>.xlsx</code>) en carpetas <code>CAT/</code> y <code>REG/</code></td><td>SQLite (<code>taller.db</code>) — un solo archivo</td></tr>
  <tr><td>Capa de datos</td><td>pandas + openpyxl (lectura/escritura directa de Excel)</td><td><code>db.py</code> (módulo SQL con funciones CRUD)</td></tr>
  <tr><td>Usuarios</td><td>Configurables por variables de entorno</td><td>Tabla <code>USUARIOS</code> en SQLite con contraseñas hasheadas</td></tr>
  <tr><td>Roles</td><td>Un solo nivel de acceso</td><td>Cuatro niveles: superusuario, administrador, supervisor, usuario</td></tr>
  <tr><td>Permisos</td><td>Sin restricciones por sección</td><td>Permisos modulares por sección (campo <code>secciones</code> por usuario)</td></tr>
  <tr><td>Sesiones</td><td>Básicas (sin expiración)</td><td>Con timeout configurable (default 30 min) y aviso al usuario</td></tr>
  <tr><td>Acceso</td><td><code>http://localhost:5000</code></td><td><code>https://yekflow.com</code> vía Cloudflare Tunnel</td></tr>
  <tr><td>Concurrencia</td><td>No recomendada (Excel no soporta escritura simultánea)</td><td>SQLite soporta lecturas simultáneas; escrituras se serializan</td></tr>
  <tr><td>Inicio</td><td>Manual (<code>python app.py</code>)</td><td>Automático vía <code>systemd</code> al encender la PC</td></tr>
</table>

<h4>¿Por qué dos versiones?</h4>
<p>La versión local usa Excel para que puedas ver y editar datos directamente en hojas de cálculo
durante el desarrollo. La versión de producción usa SQLite porque es más robusta, rápida y segura
para un servidor que corre 24/7 con múltiples usuarios accediendo al mismo tiempo.</p>

<h4>¿Cómo se sincronizan?</h4>
<p><strong>No se sincronizan automáticamente.</strong> Son bases de datos completamente independientes.
Los cambios de código (templates, CSS, Python) se transfieren usando el paquete ZIP del servidor.
Los datos (materiales, proyectos, avances) viven solo en su respectivo entorno.</p>

{warn('Nunca modifiques <code>taller.db</code> directamente con un editor de SQLite externo mientras el servidor está corriendo. Usa siempre la interfaz web o detén el servicio primero.')}

{sub('arquitectura-prod', '10.4 Arquitectura de producción')}
<pre>
PC Windows (desarrollo)               PC Ubuntu (servidor 24/7)
┌────────────────────┐                ┌─────────────────────────┐
│ app.py (Flask)     │                │ app_web.py (Flask)      │
│ Archivos Excel     │  ZIP ────────► │ taller.db (SQLite)      │
│ localhost:5000     │                │ puerto 5000             │
└────────────────────┘                └──────────┬──────────────┘
                                                 │
                                      Cloudflare Tunnel (gratis)
                                                 │
                                      ┌──────────▼──────────────┐
                                      │   yekflow.com (HTTPS)   │
                                      │   Acceso desde internet │
                                      └─────────────────────────┘
</pre>
<ul>
  <li><strong>PC Windows</strong>: desarrollo y pruebas. Usa archivos Excel como base de datos.</li>
  <li><strong>PC Ubuntu</strong>: servidor de producción 24/7. Usa SQLite (<code>taller.db</code>).</li>
  <li><strong>Los datos NO se sincronizan</strong> entre ambos entornos. Son bases independientes.</li>
  <li><strong>Cloudflare Tunnel</strong>: conexión segura sin abrir puertos en el router.</li>
</ul>

<hr class="section-divider">

<!-- ══════════════════════════════ GLOSARIO ══════════════════════════════ -->
{sec('glosario', '11. Glosario')}
<table>
  <tr><th>Término</th><th>Significado</th></tr>
  <tr><td>OP</td><td>Orden de Producción — representa una etapa de trabajo de un mueble</td></tr>
  <tr><td>Stock</td><td>Inventario actual de un material, calculado como Σ Entradas − Σ Salidas</td></tr>
  <tr><td>Traslado</td><td>Movimiento de material entre ubicaciones del almacén (no modifica el stock total)</td></tr>
  <tr><td>Semáforo</td><td>Indicador visual de estado: verde (OK), amarillo (bajo mínimo), rojo (sin stock)</td></tr>
  <tr><td>KPI</td><td>Key Performance Indicator — indicador clave en el Dashboard</td></tr>
  <tr><td>Etapa</td><td>Fase de producción de un mueble (Corte, Armado, Laqueado, etc.)</td></tr>
  <tr><td>Préstamo activo</td><td>Herramienta fuera del almacén sin fecha de devolución registrada</td></tr>
  <tr><td>CAT/</td><td>Carpeta de catálogos (datos maestros del sistema)</td></tr>
  <tr><td>REG/</td><td>Carpeta de registros transaccionales (movimientos, avances, préstamos)</td></tr>
</table>

<hr class="section-divider">

<!-- ══════════════════════════════ PREGUNTAS FRECUENTES ══════════════════════════════ -->
{sec('faq', '12. Preguntas Frecuentes')}

<h4>¿Por qué el stock de un material aparece negativo?</h4>
<p>Ocurre cuando se registraron Salidas por una cantidad mayor a las Entradas existentes.
Verifica los movimientos de ese material y agrega una Entrada inicial si corresponde.</p>

<h4>¿Puedo editar un movimiento ya registrado?</h4>
<p>Actualmente no. Para corregir un error, registra un movimiento contrario: si se ingresó
una Entrada incorrecta, registra una Salida por la misma cantidad.</p>

<h4>¿Cómo agrego una nueva etapa de producción?</h4>
<p>Las etapas se gestionan desde la hoja <strong>ETAPAS</strong> en el archivo
<code>CAT/Proyectos.xlsx</code>. Ábrelo con Excel y agrega la nueva etapa con su orden numérico.</p>

<h4>¿El sistema funciona sin internet?</h4>
<p>Sí, completamente. Solo se requiere internet para cargar las librerías externas (Bootstrap,
Chart.js) la primera vez. En redes locales sin internet, estas se pueden alojar localmente.</p>

<h4>¿Cómo respaldo los datos?</h4>
<p>Ve a <strong>Administración → Respaldo del Sistema</strong> y haz clic en <strong>Descargar backup</strong>.
El sistema genera automáticamente un <code>.zip</code> con todos los archivos Excel. Guárdalo en
OneDrive, Google Drive o un disco externo. También puedes copiar manualmente las carpetas
<code>D:\\Proyectos\\CAT\\</code> y <code>D:\\Proyectos\\REG\\</code>.</p>

<h4>¿Cómo imprimo el manual actualizado?</h4>
<p>En la sección <strong>Implementación</strong>, haz clic en el botón <strong>Actualizar e imprimir manual</strong>.
El sistema regenera el manual con la fecha actual y abre el diálogo de impresión. Elige
<em>Guardar como PDF</em> en la impresora para obtener un archivo PDF.</p>

<h4>¿Puedo usar el sistema en varias computadoras al mismo tiempo?</h4>
<p>Sí, siempre que corras el servidor Flask en una PC y los demás accedan por red local.
No es recomendable que dos personas modifiquen datos al mismo tiempo, ya que los archivos
Excel no tienen control de concurrencia.</p>

<h4>¿Cómo accedo al sistema desde otro dispositivo en la misma red?</h4>
<p>Ve a <strong>Administración → Configuración de Red</strong>. Ahí verás la IP local del servidor
(por ejemplo <code>http://192.168.1.10:5000</code>). Escribe esa dirección en el navegador del otro
dispositivo. Ambos deben estar en la misma red Wi-Fi o LAN. Si no conecta, verifica que el firewall
de Windows permita el puerto 5000.</p>

<h4>¿Cómo accedo desde fuera de la red (internet)?</h4>
<p>Usa el <strong>Túnel Cloudflare</strong> en <strong>Administración → Configuración de Red</strong>.
Instala <code>cloudflared</code>, inicia el túnel y comparte la URL pública generada. La URL es temporal
y cambia con cada inicio del túnel.</p>

<h4>¿Puedo desactivar la solicitud de usuario y contraseña?</h4>
<p>Sí, desde <strong>Administración → Configuración de Red → Autenticación</strong>.
El cambio es inmediato. Solo desactívala en redes completamente privadas. Si el túnel de Cloudflare está activo,
mantén la autenticación encendida para proteger el acceso.</p>

<h4>¿Cómo cambio el usuario y contraseña del sistema?</h4>
<p>Ve a <strong>Administración → Gestión de Usuarios</strong>. Haz clic en el ícono de edición del usuario
que quieres modificar, escribe la nueva contraseña y guarda. Los valores por defecto del usuario
administrador son <code>admin</code> / <code>taller2024</code>.</p>

<h4>¿Cómo actualizo el sistema en producción (servidor)?</h4>
<p>Ve a la sección <strong>10. Servidor y Producción</strong> de este manual. En resumen: genera el
paquete ZIP desde Administración, cópialo al servidor Ubuntu y ejecuta
<code>sudo actualizar-taller /ruta/al/archivo.zip</code>.</p>

<h4>¿Cómo veo quién está usando el sistema en producción?</h4>
<p>En la terminal del servidor Ubuntu, ejecuta <code>journalctl -u taller -f</code> para ver
el tráfico en tiempo real. Cada solicitud HTTP aparecerá con la hora, ruta y código de respuesta.</p>

<h4>¿Qué hago si el servidor muestra "Forbidden" después de reiniciar?</h4>
<p>Esto ocurre si la sesión del navegador quedó corrupta. Limpia las cookies del navegador
o abre una ventana de incógnito e inicia sesión de nuevo. El sistema detecta sesiones corruptas
y redirige al login automáticamente.</p>
"""

TOC_ITEMS = [
    ("intro", "1. Introducción", "h2"),
    ("requisitos", "1.1 Requisitos", "h3"),
    ("inicio", "1.2 Iniciar el sistema", "h3"),
    ("estructura", "1.3 Estructura de archivos", "h3"),
    ("dashboard", "2. Dashboard", "h2"),
    ("almacen", "3. Almacén", "h2"),
    ("stock", "3.1 Stock Actual", "h3"),
    ("movimientos", "3.2 Registrar Movimiento", "h3"),
    ("catalogo-mat", "3.3 Catálogo de Materiales", "h3"),
    ("mapa-ubic", "3.4 Mapa de Ubicaciones", "h3"),
    ("herramientas", "4. Herramientas", "h2"),
    ("prestamo", "4.1 Registrar Préstamo", "h3"),
    ("devolucion", "4.2 Registrar Devolución", "h3"),
    ("cat-herr", "4.3 Catálogo e Inventario", "h3"),
    ("proyectos", "5. Proyectos", "h2"),
    ("jerarquia", "5.1 Jerarquía", "h3"),
    ("muebles", "5.2 Muebles", "h3"),
    ("ops", "5.3 Órdenes de Producción", "h3"),
    ("etapas", "5.4 Etapas", "h3"),
    ("avance", "6. Avance de Obras", "h2"),
    ("registrar-av", "6.1 Registrar Avance", "h3"),
    ("vistas-av", "6.2 Vistas", "h3"),
    ("filtros-av", "6.3 Filtros", "h3"),
    ("imprimir-av", "6.4 Hoja Imprimible", "h3"),
    ("dash-av", "6.5 Dashboard de Avance", "h3"),
    ("empleados", "7. Empleados", "h2"),
    ("implementacion", "8. Implementación", "h2"),
    ("flujo-imp", "8.1 Flujo recomendado", "h3"),
    ("forms-disponibles", "8.2 Formularios", "h3"),
    ("admin", "9. Administración", "h2"),
    ("reset", "9.1 Borrar datos", "h3"),
    ("backup", "9.2 Respaldo / Restauración", "h3"),
    ("editor-bd", "9.3 Editor de Base de Datos", "h3"),
    ("red", "9.4 Configuración de Red", "h3"),
    ("servidor", "10. Servidor y Producción", "h2"),
    ("flujo-deploy", "10.1 Flujo de actualización", "h3"),
    ("comandos-servidor", "10.2 Comandos del servidor", "h3"),
    ("diferencias", "10.3 Local vs Producción", "h3"),
    ("arquitectura-prod", "10.4 Arquitectura", "h3"),
    ("glosario", "11. Glosario", "h2"),
    ("faq", "12. Preguntas Frecuentes", "h2"),
]


def build_html():
    """Construye y devuelve el HTML completo del manual (llamable desde Flask)."""
    toc_html = '<div class="toc-title">Contenido</div>\n'
    for anchor, label, level in TOC_ITEMS:
        toc_html += f'<a href="#{anchor}" class="{level}">{label}</a>\n'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Manual de Usuario — Sistema de Taller</title>
  <style>{STYLE}</style>
</head>
<body>
<div class="wrapper">
  <nav class="toc">{toc_html}</nav>
  <main class="content">{CONTENT}</main>
</div>
</body>
</html>"""


if __name__ == "__main__":
    html = build_html()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK - Manual generado exitosamente:")
    print(f"   {OUTPUT}")
    print(f"\n   Abrelo en tu navegador con doble clic o arrastralo a Chrome/Edge.")
