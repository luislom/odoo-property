# update.sh — en la raíz del proyecto
#!/usr/bin/env bash
set -e                      # aborta si algo falla

DB="${DB:-odoo_dev}"           # se puede sobreescribir: DB=otra ./update.sh
MOD="${1:-all}"             # módulo opcional; por defecto, todos

echo "→ Actualizando '$MOD' en la base '$DB'..."
docker compose stop odoo
docker compose run --rm odoo odoo -d "$DB" -u "$MOD" --stop-after-init
docker compose start odoo
echo "✓ Listo. http://localhost:8069"
