#!/bin/bash
#
# token_monitor.sh v2.0 - Monitoreo híbrido de token usage
# Combina: Fiabilidad de API + Automatización + Persistencia
#
# Author: 🦊 ClawdColombia
# Boring Builder Protocol - Principle 2: Sobrevive sleep/offline
#
# USAGE:
#   ./token_monitor.sh              # Check con mejor método disponible
#   ./token_monitor.sh --api        # Fuerza uso de OpenClaw API
#   ./token_monitor.sh --cli        # Fuerza uso de CLI (clawdbot status)
#   ./token_monitor.sh --watch      # Watch mode (cada 60s)
#   ./token_monitor.sh --quiet      # Solo exit code
#   ./token_monitor.sh --dashboard  # Muestra histórico
#
# EXIT CODES:
#   0 - OK (< 80%)
#   1 - Warning (80-89%)
#   2 - Critical (>= 90%)
#   3 - Error en obtención de datos

set -euo pipefail

# Configuración
STATE_FILE="${HOME}/clawd/memory/state.json"
LOG_FILE="${HOME}/clawd/logs/token_usage.log"
HISTORY_FILE="${HOME}/clawd/logs/token_history.jsonl"
CHECKPOINT_THRESHOLD=80
ALERT_THRESHOLD=90
WATCH_INTERVAL=60

# Crear directorios
mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$HISTORY_FILE")"

# ============================================
# FUNCIONES DE OBTENCIÓN DE DATOS
# ============================================

# Método 1: API directa de OpenClaw (más fiable)
get_token_usage_api() {
    # Usa el gateway de OpenClaw si está disponible
    local gateway_url="${CLAWDBOT_GATEWAY:-http://localhost:3000}"
    local api_response
    
    # Intentar obtener status del gateway
    if api_response=$(curl -s "${gateway_url}/api/status" 2>/dev/null || echo ""); then
        if [[ -n "$api_response" ]]; then
            # Parsear JSON
            local percentage
            percentage=$(echo "$api_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Buscar token usage en diferentes formatos
    if 'tokens' in data and 'percentage' in data['tokens']:
        print(int(data['tokens']['percentage']))
    elif 'context' in data and 'used' in data['context'] and 'total' in data['context']:
        used = data['context']['used']
        total = data['context']['total']
        print(int(used / total * 100))
except:
    pass
" 2>/dev/null)
            
            if [[ -n "$percentage" && "$percentage" =~ ^[0-9]+$ ]]; then
                echo "$percentage"
                return 0
            fi
        fi
    fi
    return 1
}

# Método 2: CLI de clawdbot (fallback)
get_token_usage_cli() {
    local status_output
    local retry_count=0
    local max_retries=3
    
    while [[ $retry_count -lt $max_retries ]]; do
        status_output=$(clawdbot status 2>/dev/null || echo "")
        
        if [[ -n "$status_output" ]]; then
            # Múltiples patrones de parseo para robustez
            local percentage=""
            
            # Patrón 1: "Context: 92k/262k (35%)"
            percentage=$(echo "$status_output" | grep -oE 'Context:.*\([0-9]+%\)' | grep -oE '[0-9]+%' | grep -oE '[0-9]+' | head -1)
            
            # Patrón 2: "kimi-for-coding | 19k/262k (7%)"
            if [[ -z "$percentage" ]]; then
                percentage=$(echo "$status_output" | grep -oE 'kimi-for-coding.*\([0-9]+%\)' | grep -oE '[0-9]+%' | grep -oE '[0-9]+' | head -1)
            fi
            
            # Patrón 3: Buscar cualquier porcentaje en contexto de tokens
            if [[ -z "$percentage" ]]; then
                percentage=$(echo "$status_output" | grep -iE 'context.*[0-9]+k/[0-9]+k.*\([0-9]+%\)' | grep -oE '\([0-9]+%\)' | grep -oE '[0-9]+' | head -1)
            fi
            
            if [[ -n "$percentage" && "$percentage" =~ ^[0-9]+$ ]]; then
                echo "$percentage"
                return 0
            fi
        fi
        
        retry_count=$((retry_count + 1))
        [[ $retry_count -lt $max_retries ]] && sleep 1
    done
    
    return 1
}

# Método 3: Leer de state file (último recurso)
get_token_usage_cached() {
    if [[ -f "$STATE_FILE" ]]; then
        local last_usage
        last_usage=$(python3 << 'EOF' 2>/dev/null
import json, sys
try:
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    health = data.get('health', {})
    usage_str = health.get('tokens_usage', 'unknown')
    # Extraer número de "35%" o "35"
    import re
    match = re.search(r'(\d+)', str(usage_str))
    if match:
        print(match.group(1))
except:
    pass
EOF
        "$STATE_FILE")
        
        if [[ -n "$last_usage" && "$last_usage" =~ ^[0-9]+$ ]]; then
            echo "$last_usage"
            return 0
        fi
    fi
    return 1
}

# Obtener token usage con fallback automático
get_token_usage() {
    local usage=""
    local method=""
    
    # Si se especifica método forzado
    if [[ "${1:-}" == "--api" ]]; then
        usage=$(get_token_usage_api) && method="api"
    elif [[ "${1:-}" == "--cli" ]]; then
        usage=$(get_token_usage_cli) && method="cli"
    else
        # Auto-detect: intentar API primero, luego CLI, luego cache
        usage=$(get_token_usage_api) && method="api"
        
        if [[ -z "$usage" ]]; then
            usage=$(get_token_usage_cli) && method="cli"
        fi
        
        if [[ -z "$usage" ]]; then
            usage=$(get_token_usage_cached) && method="cache"
        fi
    fi
    
    if [[ -n "$usage" && "$usage" =~ ^[0-9]+$ ]]; then
        echo "$usage"
        [[ -n "$method" ]] && echo "$method" >&2
        return 0
    fi
    
    echo "unknown"
    return 1
}

# ============================================
# FUNCIONES DE PERSISTENCIA
# ============================================

update_state() {
    local usage=$1
    local method=$2
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    if [[ -f "$STATE_FILE" ]]; then
        python3 << EOF
import json
import sys

try:
    with open('$STATE_FILE', 'r') as f:
        data = json.load(f)
    
    if 'health' not in data:
        data['health'] = {}
    
    data['health']['tokens_usage'] = '${usage}%'
    data['health']['tokens_method'] = '$method'
    data['health']['last_check'] = '$timestamp'
    
    with open('$STATE_FILE', 'w') as f:
        json.dump(data, f, indent=2)
    
    print('✅ State actualizado', file=sys.stderr)
except Exception as e:
    print(f'Error actualizando state: {e}', file=sys.stderr)
EOF
    fi
}

log_usage() {
    local usage=$1
    local method=$2
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] Token usage: ${usage}% (method: $method)" >> "$LOG_FILE"
}

save_history() {
    local usage=$1
    local method=$2
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # JSONL para análisis posterior
    echo "{\"timestamp\":\"$timestamp\",\"usage\":$usage,\"method\":\"$method\"}" >> "$HISTORY_FILE"
    
    # Rotar si es muy grande (> 10000 líneas)
    local line_count
    line_count=$(wc -l < "$HISTORY_FILE" 2>/dev/null || echo 0)
    if [[ $line_count -gt 10000 ]]; then
        tail -n 5000 "$HISTORY_FILE" > "${HISTORY_FILE}.tmp"
        mv "${HISTORY_FILE}.tmp" "$HISTORY_FILE"
    fi
}

# ============================================
# FUNCIONES DE ALERTA Y ACCIÓN
# ============================================

check_thresholds() {
    local usage=$1
    local status=0
    
    if [[ "$usage" =~ ^[0-9]+$ ]]; then
        if [[ $usage -ge $ALERT_THRESHOLD ]]; then
            echo "🚨 ALERTA CRÍTICA: Token usage ${usage}%"
            echo "   Acción: Creando checkpoint de emergencia..."
            
            # Crear checkpoint
            if ~/clawd/tools/checkpoint-manager.sh create 2>/dev/null; then
                echo "   ✅ Checkpoint creado"
            else
                echo "   ⚠️  No se pudo crear checkpoint"
            fi
            
            # Notificar si hay webhook configurado
            if [[ -n "${NOTIFY_WEBHOOK:-}" ]]; then
                curl -s -X POST -H "Content-Type: application/json" \
                    -d "{\"text\":\"🚨 Token usage crítico: ${usage}%\"}" \
                    "$NOTIFY_WEBHOOK" > /dev/null 2>&1 || true
            fi
            
            status=2
        elif [[ $usage -ge $CHECKPOINT_THRESHOLD ]]; then
            echo "⚠️  AVISO: Token usage alto (${usage}%)"
            echo "   Recomendación: Considerar crear checkpoint"
            status=1
        else
            echo "✅ OK: Token usage normal (${usage}%)"
        fi
    else
        echo "❌ Error: No se pudo obtener token usage"
        status=3
    fi
    
    return $status
}

# ============================================
# FUNCIONES DE VISUALIZACIÓN
# ============================================

show_dashboard() {
    echo "📊 TOKEN USAGE DASHBOARD"
    echo "========================"
    echo ""
    
    # Estado actual
    local current_usage current_method
    current_usage=$(get_token_usage_cached 2>/dev/null || echo "unknown")
    echo "Token usage actual: ${current_usage}%"
    echo ""
    
    # Histórico últimas 24 horas
    if [[ -f "$HISTORY_FILE" ]]; then
        echo "📈 Últimas 24h (muestras):"
        tail -n 24 "$HISTORY_FILE" 2>/dev/null | while read -r line; do
            echo "$line" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    ts = d['timestamp'][11:16]  # HH:MM
    print(f\"  {ts} - {d['usage']:>3}% ({d['method']})\")
except:
    pass
"
        done
        echo ""
    fi
    
    # Promedios
    if [[ -f "$HISTORY_FILE" ]]; then
        echo "📊 Estadísticas (últimas 100 muestras):"
        tail -n 100 "$HISTORY_FILE" | python3 << 'EOF'
import json, sys
usages = []
for line in sys.stdin:
    try:
        d = json.loads(line)
        usages.append(d['usage'])
    except:
        pass
if usages:
    print(f"  Promedio: {sum(usages)/len(usages):.1f}%")
    print(f"  Mínimo:   {min(usages)}%")
    print(f"  Máximo:   {max(usages)}%")
EOF
    fi
    
    # Logs recientes
    echo ""
    echo "📝 Logs recientes:"
    tail -n 5 "$LOG_FILE" 2>/dev/null || echo "  (sin logs)"
}

watch_mode() {
    echo "👁️  Watch mode iniciado (Ctrl+C para salir)"
    echo "Actualizando cada ${WATCH_INTERVAL}s"
    echo ""
    
    while true; do
        clear
        date
        echo ""
        main_check
        echo ""
        echo "Próxima actualización en ${WATCH_INTERVAL}s..."
        sleep $WATCH_INTERVAL
    done
}

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

main_check() {
    local method_flag="${1:-}"
    
    # Obtener datos
    local result
    result=$(get_token_usage "$method_flag")
    local exit_code=$?
    
    if [[ $exit_code -ne 0 || "$result" == "unknown" ]]; then
        echo "❌ Error: No se pudo obtener token usage"
        return 3
    fi
    
    local usage=$result
    local method=""
    
    # Leer método de stderr si está disponible
    if [[ -s /dev/stderr ]]; then
        method=$(cat /dev/stderr 2>/dev/null | tail -1)
    fi
    [[ -z "$method" ]] && method="unknown"
    
    # Persistir datos
    update_state "$usage" "$method"
    log_usage "$usage" "$method"
    save_history "$usage" "$method"
    
    # Verificar thresholds
    check_thresholds "$usage"
    return $?
}

# ============================================
# MAIN
# ============================================

case "${1:-}" in
    --help|-h)
        echo "Token Monitor v2.0 - Uso:"
        echo "  $0                  # Check con auto-detección"
        echo "  $0 --api            # Fuerza uso de API"
        echo "  $0 --cli            # Fuerza uso de CLI"
        echo "  $0 --watch          # Modo watch (cada 60s)"
        echo "  $0 --dashboard      # Muestra dashboard"
        echo "  $0 --quiet          # Solo exit code"
        ;;
    --quiet|-q)
        main_check > /dev/null 2>&1
        exit $?
        ;;
    --watch|-w)
        watch_mode
        ;;
    --dashboard|-d)
        show_dashboard
        ;;
    --api|--cli)
        echo "📊 Token Monitor v2.0"
        echo "===================="
        main_check "$1"
        exit $?
        ;;
    *)
        echo "📊 Token Monitor v2.0"
        echo "===================="
        main_check
        echo ""
        echo "Uso: $0 [--api|--cli|--watch|--dashboard|--quiet|--help]"
        exit $?
        ;;
esac
