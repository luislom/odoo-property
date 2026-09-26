# odooRealEstate — Odoo 19 con Docker y Dev Containers

Guía de referencia del proyecto: cómo está montado, qué herramientas usa, cómo arrancarlo, cómo desarrollar módulos y cómo trabajar con la base de datos.

---

## Índice

1. [Idea general](#1-idea-general)
2. [Herramientas](#2-herramientas)
3. [Estructura del proyecto](#3-estructura-del-proyecto)
4. [Primera vez (en un equipo nuevo)](#4-primera-vez-en-un-equipo-nuevo)
5. [Dev Containers (VS Code dentro del contenedor)](#5-dev-containers-vs-code-dentro-del-contenedor)
6. [Crear la base de datos en Odoo](#6-crear-la-base-de-datos-en-odoo)
7. [Desarrollo de módulos](#7-desarrollo-de-módulos)
8. [Qué hacer según el tipo de cambio](#8-qué-hacer-según-el-tipo-de-cambio)
9. [Interactuar con la base de datos](#9-interactuar-con-la-base-de-datos)
10. [Backups y restauración](#10-backups-y-restauración)
11. [Comandos de Docker](#11-comandos-de-docker)
12. [Git y trabajo en equipo](#12-git-y-trabajo-en-equipo)
13. [Problemas conocidos y soluciones](#13-problemas-conocidos-y-soluciones)
14. [Seguridad antes de producción](#14-seguridad-antes-de-producción)

---

## 1. Idea general

El repositorio **no contiene Odoo**. Solo contiene:

- Los **módulos propios** (`addons/`).
- La **configuración** para levantar Odoo y PostgreSQL con Docker.
- La configuración de **Dev Containers** para programar dentro del contenedor.

Odoo se descarga como imagen oficial de Docker (`odoo:19.0`). Por eso el repo pesa muy poco y se puede hacer `push` sin problemas, clonar en cualquier equipo y colaborar.

Los datos (base de datos y archivos adjuntos) viven en **volúmenes de Docker**, fuera del repo. No se suben a git.

```
Tu Mac
├── Repo (git)  ──────────────►  addons/, config/, docker-compose.yml, .devcontainer/
└── Docker
    ├── Contenedor "odoo" (Odoo 19 + Python)  ◄── monta addons/ y config/
    │     └── volumen odoo-data  (filestore, sesiones)
    └── Contenedor "db"   (PostgreSQL 16)
          └── volumen db-data    (la base de datos)
```

---

## 2. Herramientas

| Herramienta | Para qué se usa |
|---|---|
| **Docker Desktop** | Ejecuta los contenedores de Odoo y PostgreSQL. |
| **Docker Compose** | Define y levanta ambos servicios con un solo comando (`docker-compose.yml`). |
| **Imagen `odoo:19.0`** | Odoo 19 oficial con Python y todas sus dependencias ya instaladas. |
| **Imagen `postgres:16`** | Base de datos que usa Odoo. |
| **VS Code** | Editor. |
| **Extensión Dev Containers** | Conecta VS Code al interior del contenedor de Odoo: autocompletado, terminal y depuración usan el Python del contenedor. |
| **Extensiones dentro del contenedor** | Python, Pylance, Python Debugger y XML (se instalan solas al abrir el Dev Container). |
| **Git + repo privado** | Control de versiones del código propio. |
| **Odoo shell** | Consola de Python con el ORM de Odoo cargado. |
| **psql** | Cliente de línea de comandos de PostgreSQL (ya viene en la imagen de Odoo). |
| **SQLTools / DBeaver / pgAdmin** (opcional) | Ver la base de datos con interfaz gráfica. |

> **No se necesita `venv`**: el Python que ejecuta el código es el del contenedor.

---

## 3. Estructura del proyecto

```
odooRealEstate/
├── .devcontainer/
│   ├── devcontainer.json                 # Configuración de Dev Containers
│   └── docker-compose.devcontainer.yml   # Añadidos solo para Dev Containers
├── addons/                               # Módulos propios (esto es lo que se programa)
├── config/
│   └── odoo.conf                         # Configuración de Odoo
├── docker-compose.yml                    # Servicios: odoo + db
├── .gitignore
└── README.md
```

### `docker-compose.yml`

| Servicio | Imagen | Puerto | Volúmenes |
|---|---|---|---|
| `db` | `postgres:16` | (interno 5432) | `db-data` → datos de PostgreSQL |
| `odoo` | `odoo:19.0` | `8069:8069` | `./addons` → `/mnt/extra-addons`, `./config` → `/etc/odoo`, `odoo-data` → `/var/lib/odoo` |

Credenciales de PostgreSQL en desarrollo: usuario `odoo`, contraseña `odoo`, host `db`.

### `config/odoo.conf`

| Opción | Significado |
|---|---|
| `addons_path = /mnt/extra-addons` | Dónde busca Odoo los módulos propios (los oficiales ya los conoce). |
| `data_dir = /var/lib/odoo` | Filestore y sesiones. |
| `admin_passwd` | **Master Password**: la que pide el gestor de bases de datos para crear, borrar o restaurar bases. |
| `dev_mode = reload,xml` | Recarga automática al guardar archivos Python y vistas XML. |

> Cualquier cambio en `odoo.conf` requiere `docker compose restart odoo`.

### `.devcontainer/`

- `devcontainer.json`: usa los dos archivos compose, se conecta al servicio `odoo`, abre la carpeta `/workspace`, usa el usuario `odoo`, instala extensiones y fija bash como terminal.
- `docker-compose.devcontainer.yml`: monta el repo completo en `/workspace` y define `SHELL=/bin/bash`.

> Las rutas relativas de ese archivo se resuelven desde la **raíz del proyecto** (donde está el primer compose), por eso el volumen es `.:/workspace` y no `..:/workspace`.

---

## 4. Primera vez (en un equipo nuevo)

1. Instalar **Docker Desktop** y **VS Code** con la extensión **Dev Containers**.
2. Clonar el repo:
   ```bash
   git clone <url-del-repo>
   cd odooRealEstate
   ```
3. Abrir la carpeta en VS Code → `F1` → **Dev Containers: Reopen in Container**.
   (La primera vez tarda unos minutos: descarga imágenes e instala extensiones.)
4. Abrir <http://localhost:8069> y crear la base de datos (ver sección 6).

Sin VS Code también funciona:
```bash
docker compose up -d
```

---

## 5. Dev Containers (VS Code dentro del contenedor)

**Cómo saber que estás dentro:** abajo a la izquierda aparece `Dev Container: Odoo 19`.

**Qué cambia estando dentro:**
- El explorador muestra `/workspace` (el repo completo).
- La terminal integrada es una terminal **dentro del contenedor de Odoo**: se pueden usar `odoo`, `psql`, etc. sin `docker compose exec`.
- `from odoo import models, fields, api` se autocompleta porque Pylance ve el código de Odoo en `/usr/lib/python3/dist-packages`.

**Comandos de VS Code (`F1`):**

| Comando | Cuándo |
|---|---|
| **Dev Containers: Reopen in Container** | Abrir el proyecto dentro del contenedor. |
| **Dev Containers: Reopen Folder Locally** | Volver a trabajar fuera del contenedor. |
| **Dev Containers: Rebuild Container** | Tras cambiar `devcontainer.json` o los archivos compose. |
| **Dev Containers: Rebuild and Reopen in Container** | Igual que el anterior, desde fuera del contenedor. |

> Los archivos siguen en el Mac; el contenedor solo los ve a través del volumen. Borrar el contenedor no borra el código.

---

## 6. Crear la base de datos en Odoo

En <http://localhost:8069> (o `/web/database/manager`):

| Campo | Qué poner |
|---|---|
| **Master Password** | El valor de `admin_passwd` en `config/odoo.conf`. |
| **Database Name** | Un nombre nuevo, p. ej. `odoo_dev` (minúsculas, números y `_`). |
| **Email / Password** | Usuario administrador de esa base (con el que se inicia sesión). |
| **Demo Data** | Marcar si se quieren datos de ejemplo (útil para pruebas). |

> **"Access Denied"** = Master Password incorrecta. Revisar `admin_passwd` y reiniciar Odoo si se cambió.

Se pueden tener varias bases (p. ej. `odoo_dev` y `odoo_pruebas`).

**Modo desarrollador:** Ajustes → al final "Activar el modo desarrollador", o añadir `?debug=1` a la URL (`?debug=assets` para depurar JS/CSS sin caché).

---

## 7. Desarrollo de módulos

> Todos los comandos de esta sección se ejecutan en la **terminal de VS Code dentro del Dev Container**.
> Desde el Mac, anteponer `docker compose exec odoo` (o usar `docker compose run --rm odoo ...`).

### Crear un módulo nuevo

```bash
odoo scaffold nombre_modulo /mnt/extra-addons
```

Genera la estructura básica:

```
addons/nombre_modulo/
├── __init__.py
├── __manifest__.py      # nombre, versión, dependencias, archivos de datos
├── controllers/
├── demo/
├── models/              # modelos (clases Python)
├── security/
│   └── ir.model.access.csv   # permisos (obligatorio para ver los modelos)
└── views/               # vistas XML, menús, acciones
```

Luego en Odoo (modo desarrollador): **Aplicaciones → Actualizar lista de aplicaciones → buscar el módulo → Instalar**.

### Instalar / actualizar un módulo desde la terminal

```bash
# Instalar
odoo -i nombre_modulo -d odoo_dev --db_host db --db_user odoo --db_password odoo --stop-after-init --no-http

# Actualizar (tras cambiar modelos, manifest, seguridad, datos)
odoo -u nombre_modulo -d odoo_dev --db_host db --db_user odoo --db_password odoo --stop-after-init --no-http
```

| Opción | Significado |
|---|---|
| `-i` | Instalar módulo(s) (separar varios con comas). |
| `-u` | Actualizar módulo(s). `-u all` actualiza todos (lento). |
| `-d` | Base de datos sobre la que actuar. |
| `--stop-after-init` | Termina al acabar, en vez de quedarse como servidor. |
| `--no-http` | No intenta abrir el puerto 8069 (ya lo usa el servidor en marcha). |

Si el navegador no refleja la actualización: `docker compose restart odoo` (desde el Mac).

> **Truco para acortar comandos:** añadir en `config/odoo.conf`
> ```
> db_host = db
> db_user = odoo
> db_password = odoo
> ```
> y reiniciar. Después basta con `odoo -u nombre_modulo -d odoo_dev --stop-after-init --no-http` (y lo mismo para `odoo shell -d odoo_dev`).

### Ver logs

```bash
docker compose logs -f odoo        # desde el Mac
```
Los errores de Python (tracebacks) aparecen ahí.

---

## 8. Qué hacer según el tipo de cambio

| Cambio | Acción |
|---|---|
| Lógica Python (métodos) | Nada: se recarga solo (`dev_mode = reload`). |
| Vista XML ya existente | Recargar el navegador (`dev_mode = xml`). |
| Campos o modelos nuevos | Actualizar el módulo (`-u` o botón **Actualizar** en Aplicaciones). |
| Archivo nuevo en `__manifest__.py` (vistas, seguridad, datos) | Actualizar el módulo. |
| `ir.model.access.csv` | Actualizar el módulo. |
| Módulo nuevo | Actualizar lista de aplicaciones → Instalar. |
| JS / CSS / QWeb del frontend | Recargar con `?debug=assets`. |
| `config/odoo.conf` | `docker compose restart odoo`. |
| `docker-compose.yml` | `docker compose up -d` (recrea lo que cambió). |
| `.devcontainer/*` | **Dev Containers: Rebuild Container**. |

> No hace falta apagar y encender los contenedores en el trabajo diario.

---

## 9. Interactuar con la base de datos

### 9.1 Odoo shell (recomendado para desarrollar)

Consola de Python con el entorno de Odoo (`env`) cargado.

```bash
odoo shell -d odoo_dev --db_host db --db_user odoo --db_password odoo --no-http
```

Salir con `Ctrl + D` o `exit()`.

**Chuleta del ORM:**

```python
# Obtener un modelo
Partner = env['res.partner']

# Buscar
Partner.search([])                                  # todos
Partner.search([('is_company', '=', True)], limit=5)
Partner.search_count([('country_id.code', '=', 'CO')])
Partner.browse(1)                                    # por id

# Leer
p = Partner.browse(1)
p.name, p.email
Partner.search([], limit=5).mapped('name')           # lista de nombres
Partner.search_read([('is_company', '=', True)], ['name', 'email'], limit=5)

# Crear
nuevo = Partner.create({'name': 'Cliente de prueba', 'email': 'prueba@ejemplo.com'})

# Modificar
nuevo.write({'phone': '3000000000'})
nuevo.name = 'Cliente renombrado'

# Borrar
nuevo.unlink()

# ¡Guardar cambios! (sin esto, al salir se descartan)
env.cr.commit()

# Deshacer lo no guardado
env.cr.rollback()

# Información útil
env.user                         # usuario actual (superusuario en el shell)
env['ir.module.module'].search([('name', '=', 'nombre_modulo')]).state
env['ir.model'].search([('model', 'like', 'estate')]).mapped('model')

# SQL desde el shell (solo lectura, preferiblemente)
env.cr.execute("SELECT id, name FROM res_partner LIMIT 5")
env.cr.fetchall()
```

**Dominios** (filtros de `search`): lista de tuplas `(campo, operador, valor)`.
Operadores comunes: `=`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `not in`, `like`, `ilike` (sin distinguir mayúsculas), `child_of`.
Combinar con `'|'` (OR) y `'&'` (AND, por defecto) en notación prefija:
```python
[('state', '=', 'new'), '|', ('price', '>', 1000), ('garden', '=', True)]
```

### 9.2 psql (SQL directo)

```bash
psql -h db -U odoo odoo_dev
# contraseña: odoo   (o sin pedirla: PGPASSWORD=odoo psql -h db -U odoo odoo_dev)
```

Desde el Mac, sin Dev Container:
```bash
docker compose exec db psql -U odoo odoo_dev
```

**Comandos de psql:**

| Comando | Qué hace |
|---|---|
| `\l` | Listar bases de datos. |
| `\c odoo_dev` | Conectarse a otra base. |
| `\dt` | Listar tablas. |
| `\dt estate*` | Tablas que empiezan por `estate`. |
| `\d res_partner` | Estructura de una tabla (columnas, tipos, índices). |
| `\x` | Alternar vista expandida (útil con tablas anchas). |
| `\q` | Salir. |

**Nombres de tablas:** el modelo `estate.property` se guarda en la tabla `estate_property` (puntos → guiones bajos).
Las relaciones `many2many` usan tablas intermedias (p. ej. `estate_property_estate_property_tag_rel`).

```sql
SELECT id, name, email FROM res_partner ORDER BY id DESC LIMIT 10;
SELECT name, state FROM ir_module_module WHERE name LIKE 'estate%';
```

> **Regla:** usar SQL para **consultar**; para **modificar** datos usar el ORM (shell o interfaz).
> Un `UPDATE` directo se salta campos calculados, restricciones, permisos y la caché de Odoo.

### 9.3 Interfaz gráfica

**Opción A — SQLTools en VS Code (sin exponer puertos):**
instalar dentro del Dev Container las extensiones *SQLTools* y *SQLTools PostgreSQL/Cockroach Driver*, y crear una conexión con:

| Campo | Valor |
|---|---|
| Host | `db` |
| Puerto | `5432` |
| Base de datos | `odoo_dev` |
| Usuario / contraseña | `odoo` / `odoo` |

**Opción B — DBeaver, pgAdmin, TablePlus (en el Mac):**
añadir al servicio `db` en `docker-compose.yml`:
```yaml
    ports:
      - "5433:5432"
```
Aplicar con `docker compose up -d` y conectar a `localhost:5433`, usuario `odoo`, contraseña `odoo`, base `odoo_dev`.
(Se usa `5433` para no chocar con un PostgreSQL local.)

### 9.4 Desde la interfaz de Odoo (modo desarrollador)

**Ajustes → Técnico**:
- **Modelos**: campos de cada modelo.
- **Vistas**: vistas XML cargadas y su herencia.
- **Acciones / Menús**: navegación.
- **Parámetros del sistema**: valores de configuración.
- **Tareas programadas** (cron).

Con el icono del bicho (debug) en cualquier formulario: **Ver campos**, **Ver metadatos** (id externo del registro) y **Editar vista**.

---

## 10. Backups y restauración

### Recomendado: gestor de Odoo

<http://localhost:8069/web/database/manager>
- **Backup** → formato `zip` (incluye base de datos **y** filestore). Pide la Master Password.
- **Restore** → subir el `.zip`. Elegir "This database is a copy" si se va a usar en paralelo a la original.

Es la forma de **llevar datos de un equipo a otro** (los datos no viajan por git).

### Solo SQL (sin adjuntos)

```bash
# Exportar (desde el Mac)
docker compose exec db pg_dump -U odoo odoo_dev > backup_odoo_dev.sql

# Importar en una base nueva
docker compose exec db createdb -U odoo odoo_copia
docker compose exec -T db psql -U odoo odoo_copia < backup_odoo_dev.sql
```

> Los backups (`*.sql`, `*.zip`, `*.dump`) están en `.gitignore`: no se suben al repo.

---

## 11. Comandos de Docker

Ejecutar desde la carpeta del proyecto, **en el Mac**:

| Comando | Qué hace |
|---|---|
| `docker compose up -d` | Levanta los servicios en segundo plano (y aplica cambios del compose). |
| `docker compose ps` | Estado de los contenedores. |
| `docker compose logs -f odoo` | Logs de Odoo en vivo (`Ctrl + C` para salir). |
| `docker compose restart odoo` | Reinicia solo Odoo. |
| `docker compose stop` | Detiene sin borrar contenedores. |
| `docker compose down` | Detiene y borra contenedores (**los datos se conservan**). |
| `docker compose down -v` | ⚠️ Borra también los volúmenes: **se pierden base de datos y filestore**. |
| `docker compose exec odoo bash` | Abre una terminal dentro del contenedor de Odoo. |
| `docker compose exec db psql -U odoo odoo_dev` | psql desde el Mac. |
| `docker compose pull` | Descarga la última versión de las imágenes (`odoo:19.0` recibe parches). |
| `docker volume ls` | Lista volúmenes. |
| `docker system df` | Espacio usado por Docker. |

Tras `docker compose pull`, aplicar con `docker compose up -d`.

---

## 12. Git y trabajo en equipo

Qué va al repo: `addons/`, `config/`, `docker-compose.yml`, `.devcontainer/`, `.gitignore`, `README.md`.
Qué **no** va: base de datos, filestore, backups, `__pycache__`, `.env`, carpetas de IDE.

Flujo básico:

```bash
git status
git add .
git commit -m "estate: añade modelo de ofertas"
git push
```

En otro equipo o para un colaborador: `git pull` y, si cambiaron `.devcontainer/` o el compose, **Rebuild Container**. Si cambiaron modelos de un módulo, actualizarlo con `-u`.

Recomendaciones:
- Una rama por funcionalidad (`git checkout -b feature/ofertas`) y pull request al repo privado.
- Subir la versión en `__manifest__.py` (`'version': '19.0.1.0.1'`) al cambiar estructura de datos.

---

## 13. Problemas conocidos y soluciones

| Síntoma | Causa | Solución |
|---|---|---|
| El push falla por tamaño | Se intentó subir el código de Odoo completo | Versionar solo `addons/` y configuración (este esquema). |
| `Database creation error: Access Denied` | Master Password incorrecta | Usar el valor de `admin_passwd`; reiniciar Odoo si se editó. |
| `Workspace does not exist` al abrir el Dev Container | El contenedor no tenía el volumen `/workspace` (ya estaba corriendo antes) | `docker compose down` en el Mac → **Rebuild and Reopen in Container**. |
| VS Code abre la carpeta padre con todos los proyectos | Volumen `..:/workspace` | Usar `.:/workspace` (las rutas se resuelven desde la raíz del proyecto). |
| `The terminal process "/usr/sbin/nologin" failed to launch` | El usuario `odoo` de la imagen no tiene shell | `SHELL: /bin/bash` en `docker-compose.devcontainer.yml` + perfil bash en `devcontainer.json` + rebuild. |
| `An error occurred setting up the container` en menos de 1 s | Error de sintaxis en YAML (tabuladores/sangría) o JSON (comas) | Revisar los archivos de `.devcontainer/`; mirar el log más arriba del "Command failed". |
| El módulo no aparece en Aplicaciones | No se actualizó la lista, o falta `__manifest__.py` / `__init__.py` | Modo desarrollador → Actualizar lista de aplicaciones; quitar el filtro "Aplicaciones". |
| El modelo existe pero no se ve / error de acceso | Falta `security/ir.model.access.csv` o no está en el manifest | Añadirlo al manifest y actualizar el módulo. |
| Un cambio en Python no se refleja | La recarga automática no detectó el archivo | `docker compose restart odoo`. |
| Error al guardar archivos (permisos) | Solo en Linux: UID distinto entre host y contenedor | Ajustar permisos o configurar `updateRemoteUserUID`. |
| Puerto 8069 ocupado | Otro Odoo corriendo en el Mac | Detenerlo o cambiar a `"8070:8069"` en el compose. |

---

## 14. Seguridad antes de producción

Esta configuración es **para desarrollo**. Antes de usarla en un servidor:

- Cambiar `admin_passwd` y las contraseñas de PostgreSQL (idealmente en un archivo `.env`, que ya está en `.gitignore`).
- En `odoo.conf`: quitar `dev_mode`, añadir `list_db = False` y `proxy_mode = True`.
- Poner Odoo detrás de un proxy inverso con HTTPS (nginx, Traefik, Caddy).
- No exponer el puerto de PostgreSQL.
- Programar backups periódicos.