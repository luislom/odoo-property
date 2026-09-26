# Mi proyecto Odoo 19

## Requisitos
- Docker y Docker Compose (en Windows: Docker Desktop con WSL2)

## Arrancar
```bash
git clone <url-de-tu-repo>
cd mi-proyecto-odoo
docker compose up -d
```
Abre http://localhost:8069 y crea una base de datos.

## Crear un módulo nuevo
```bash
docker compose exec odoo odoo scaffold mi_modulo /mnt/extra-addons
```
Luego en Odoo: activa el modo desarrollador → Aplicaciones → Actualizar lista de aplicaciones.

## Actualizar un módulo tras cambios en modelos
```bash
docker compose run --rm odoo odoo -u mi_modulo -d NOMBRE_BD --stop-after-init
docker compose restart odoo
```

## Comandos útiles
- Ver logs: `docker compose logs -f odoo`
- Parar: `docker compose down`
- Borrar TODO (incluida la BD): `docker compose down -v`# Mi proyecto Odoo 19

## Requisitos
- Docker y Docker Compose (en Windows: Docker Desktop con WSL2)

## Arrancar
```bash
git clone <url-de-tu-repo>
cd mi-proyecto-odoo
docker compose up -d
```
Abre http://localhost:8069 y crea una base de datos.

## Crear un módulo nuevo
```bash
docker compose exec odoo odoo scaffold mi_modulo /mnt/extra-addons
```
Luego en Odoo: activa el modo desarrollador → Aplicaciones → Actualizar lista de aplicaciones.

## Actualizar un módulo tras cambios en modelos
```bash
docker compose run --rm odoo odoo -u mi_modulo -d odoo_dev --stop-after-init
docker compose restart odoo
```

## Comandos útiles
- Ver logs: `docker compose logs -f odoo`
- Parar: `docker compose down`
- Borrar TODO (incluida la BD): `docker compose down -v`