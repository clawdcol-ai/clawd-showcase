# Finance System - REACTIVADO + Google Sheets
# Fecha: 2026-02-02
# Estado: ACTIVE

## 🎯 Resumen

Sistema de finanzas personales reactivado con integración a Gmail vía Himalaya + Google Sheets.

## 📊 Estado Actual

| Componente | Estado | Descripción |
|------------|--------|-------------|
| Email Monitor | ✅ Activo | Monitorea Bancolombia, Davivienda, Nu |
| Bank Parser | ✅ Activo | Extrae transacciones automáticamente |
| Finance Tracker | ✅ Activo | Categoriza y guarda transacciones |
| Telegram Input | ✅ Disponible | Input manual rápido |
| GSheets Sync | 🟡 En progreso | Requiere setup de Service Account |

## 🏦 Bancos Soportados

1. **Bancolombia** - Cuenta de ahorros/tarjeta débito
2. **Davivienda** - Davibank
3. **Nubank** - Tarjeta de crédito

## 🛠️ Scripts Disponibles

### Principal
- `tools/finance.sh` - Comando único para todo

### Finance/ (detallados)
- `email_monitor.sh` - Monitoreo de emails bancarios
- `parse_bank_email.py` - Parser de transacciones
- `finance-tracker.py` - Tracker principal
- `gsheet_auto_sync.py` - Sync con Google Sheets (requiere setup)
- `telegram_finance_input.py` - Input vía Telegram

## 📱 Comandos

```bash
# Gestión de transacciones
~/clawd/tools/finance.sh scan      # Buscar emails de transacciones
~/clawd/tools/finance.sh add       # Agregar gasto manual
~/clawd/tools/finance.sh report    # Reporte mensual
~/clawd/tools/finance.sh daily     # Reporte diario
~/clawd/tools/finance.sh summary   # Resumen rápido

# Google Sheets (requiere configuración previa)
~/clawd/tools/finance.sh sync      # Sincronizar con Google Sheets
```

## 📊 Estructura del Google Sheet

```
📊 Clawd - Finanzas Personales
├── 📄 Hoja 1: "Transacciones"
│   ├── Fecha | Hora | Banco | Descripción | Categoría | Tipo | Monto | Notas | ID
│   └── Se llena automáticamente desde emails
│
├── 📈 Hoja 2: "Dashboard"
│   ├── Total Ingresos | Total Gastos | Balance
│   ├── Por Categoría (tabla + fórmulas)
│   └── Gráfico circular
│
└── 🏦 Hoja 3: "Por Banco"
    ├── Resumen por institución (Bancolombia, Davivienda, Nu)
    └── Comparación de gastos/ingresos
```

## 🔧 Configuración Google Sheets

### Paso 1: Crear Service Account (Google Cloud)
1. Ve a https://console.cloud.google.com
2. Crea proyecto "Clawd Finance"
3. Habilita "Google Sheets API"
4. Crea Service Account con rol "Editor"
5. Descarga clave JSON

### Paso 2: Configurar en Clawd
```bash
# Crear directorio
mkdir -p ~/.config/clawd/credentials

# Copiar archivo descargado
cp ~/Downloads/clawd-finance-*.json ~/.config/clawd/credentials/google-sheets-service-account.json
```

### Paso 3: Crear y compartir Sheet
1. Crea nuevo Google Sheet
2. Comparte con el email del Service Account
3. Ejecuta: `~/clawd/tools/finance.sh sync`

**Guía completa:** `~/clawd/tools/finance/GOOGLE_SHEETS_SETUP.md`

## 🔐 Integración con Himalaya

- Gmail: clawdcol@gmail.com configurado
- Lectura vía IMAP: imap.gmail.com:993
- Sin dependencias OAuth complejas

## 📝 Datos Almacenados

- Transacciones: `~/clawd/finance/transactions.json`
- Categorías: `~/clawd/finance/categories.json`
- Log: `~/clawd/finance/email_monitor.log`
- Emails procesados: `~/clawd/finance/processed_emails.txt`
- Sheet ID: `~/clawd/finance/.gsheet_id`

## 💡 Categorías Predefinidas

🍽️ Alimentación | 🚗 Transporte | 🎬 Entretenimiento | 💊 Salud | 📚 Educación | 💻 Tecnología | 🏠 Gastos Fijos | 💰 Ingresos | 🏦 Ahorro | 📈 Inversiones | ✈️ Viajes | ⚪ Sin categoría

## 🎯 Próximos Pasos Sugeridos

1. **Prueba inicial:** Ejecutar `finance scan` para ver emails existentes
2. **Google Sheets:** Seguir guía de configuración
3. **Automatizar:** Agregar a HEARTBEAT.md para ejecución periódica
4. **Categorizar:** Revisar y ajustar categorías detectadas

---

**Última actualización:** 2026-02-02  
**Estado:** 🟢 Sistema operativo | 🟡 Google Sheets en configuración
