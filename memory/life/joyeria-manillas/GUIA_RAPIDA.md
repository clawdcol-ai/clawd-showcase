# Joyería Manillas - Guía Rápida

> **Instrucciones esenciales para trabajar con el proyecto de brazaletes**

---

## 🚀 Comandos Esenciales

### Generar Brazalete Nueva Talla
```bash
cd ~/clawd/memory/life/joyeria-manillas/designs
~/projects/freecad-env/freecad cmd generador_brazalete.py TALLA
```
**Tallas:** XS, S, M, L

### Visualizar STL Generado
```bash
cd ~/clawd/memory/life/joyeria-manillas/designs
python3 render_wireframe.py brazalete_M_v1.stl
```

---

## 📂 Ubicaciones Clave

| Qué | Dónde |
|-----|-------|
| Scripts generadores | `~/clawd/memory/life/joyeria-manillas/designs/` |
| Modelos 3D (.step, .stl) | `~/clawd/memory/life/joyeria-manillas/designs/` |
| FreeCAD AppImage | `~/projects/freecad-env/freecad` |
| Configuración FreeCAD | `~/projects/freecad-env/README.md` |
| Documentación completa | `~/clawd/memory/life/joyeria-manillas/README.md` |

---

## ⚙️ FreeCAD - Configuración

### Instalado en
```
~/projects/freecad-env/
├── FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage
└── freecad (symlink)
```

### Modos de Uso
- **GUI:** `~/projects/freecad-env/freecad`
- **Headless:** `~/projects/freecad-env/freecad cmd script.py`

---

## 📝 Script: generador_brazalete.py

### Qué hace
1. Calcula geometría elíptica basada en talla
2. Crea tubo elíptico con grosor de pared
3. Añade canal para liga elástica
4. Corta el "gap" de apertura
5. Exporta a .STEP y .STL

### Parámetros Modificables (en el script)
```python
TALLAS = {
    'XS': {'circumference': 150, 'gap': 35, 'width': 8, 'thickness': 3},
    'S':  {'circumference': 160, 'gap': 36, 'width': 8, 'thickness': 3},
    'M':  {'circumference': 170, 'gap': 38, 'width': 8, 'thickness': 3},
    'L':  {'circumference': 180, 'gap': 40, 'width': 8, 'thickness': 3},
}

CANAL_WIDTH = 4.0      # mm
CANAL_DEPTH = 1.5      # mm
```

---

## 🖼️ Visualización Alternativa (sin FreeCAD)

Si solo necesitas ver el diseño sin generar nuevo modelo:
```bash
cd ~/clawd/memory/life/joyeria-manillas/
python3 visualizar_maverick.py
```

Esto genera `brazalete_maverick_v2.png` con matplotlib.

---

## 🔧 Troubleshooting

### FreeCAD no inicia
```bash
# Si hay error de fuse en WSL2:
~/projects/freecad-env/freecad --appimage-extract-and-run cmd script.py
```

### Error "module Part not found"
Asegúrate de ejecutar con FreeCAD, no con python3:
```bash
# ❌ Mal
python3 generador_brazalete.py

# ✅ Bien
~/projects/freecad-env/freecad cmd generador_brazalete.py
```

---

## 📐 Especificaciones de Diseño

| Parámetro | Talla M | Descripción |
|-----------|---------|-------------|
| Circunferencia | 170mm | Interior muñeca |
| Gap | 38mm | Apertura lateral |
| Ancho (Z) | 8mm | Altura brazalete |
| Grosor pared | 3mm | Material |
| Canal ancho | 4mm | Para liga |
| Canal profundidad | 1.2mm | Hendidura |
| Ratio elipse | 1.3:1 | Ancho:Alto |

---

## ✅ Checklist de Trabajo

Antes de generar nuevo modelo:
- [ ] Revisar `generador_brazalete.py` para ajustes necesarios
- [ ] Confirmar talla deseada
- [ ] Verificar parámetros del canal

Después de generar:
- [ ] Revisar archivo .STEP (tamaño > 1KB es válido)
- [ ] Revisar archivo .STL (tamaño > 1MB es válido)
- [ ] Generar visualización con `render_wireframe.py`
- [ ] Copiar ruta para ver en Windows Explorer

---

**Actualizado:** 2026-02-02
