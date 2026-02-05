# Proyecto: Joyería - Brazalete Maverick

## 📋 Información General

**Nombre del proyecto:** joyeria-manillas  
**Tipo:** Diseño 3D paramétrico / Fabricación digital  
**Estado:** 🟢 Activo - Brazalete Elíptico con Canal para Liga

## 🎯 Objetivo

Diseñar brazaletes paramétricos tipo "Hair-Tie Hider Cuff" con apertura (gap) y canal para liga elástica.

## 🛠️ Herramientas

### CAD Principal
- **FreeCAD 1.0** (AppImage) - Modelado 3D paramétrico
- **Ubicación:** `~/projects/freecad-env/`
- **Instrucciones:** Ver `~/projects/freecad-env/README.md`

### Visualización
- **Trimesh + Matplotlib** - Renderizado rápido de STL
- **Scripts:** `render_wireframe.py`, `visualizar_brazalete.py`

## 📁 Estructura del Proyecto

```
joyeria-manillas/
├── designs/          # Scripts y modelos generados
│   ├── generador_brazalete.py    # Script principal FreeCAD
│   ├── brazalete_M_v1.step       # Modelo CAD editable
│   ├── brazalete_M_v1.stl        # Para impresión 3D
│   └── *.png                     # Renders
├── models/           # Modelos exportados adicionales
├── renders/          # Imágenes de alta calidad
├── docs/             # Documentación
│   └── software-options.md       # Alternativas de CAD
├── resources/        # Referencias y materiales
└── README.md         # Este archivo
```

## 🔧 Uso Rápido

### Generar nuevo brazalete
```bash
cd ~/clawd/memory/life/joyeria-manillas/designs
~/projects/freecad-env/freecad cmd generador_brazalete.py M
```

**Tallas disponibles:** XS (150mm), S (160mm), M (170mm), L (180mm)

### Visualizar modelo existente
```bash
cd ~/clawd/memory/life/joyeria-manillas/designs
python3 render_wireframe.py brazalete_M_v1.stl
```

## 📐 Especificaciones del Diseño

### Parámetros (Talla M - Default)
| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| Circunferencia | 170mm | Interior de la muñeca |
| Gap | 38mm | Apertura para poner/quitar |
| Ancho brazalete | 8mm | Altura (Z) |
| Grosor pared | 3mm | Material |
| Canal ancho | 4mm | Para la liga |
| Canal profundidad | 1.5mm | Hendidura |

### Geometría
- **Forma:** Elipse (ratio 1.3:1) - más ancho que alto
- **Estructura:** Tubo elíptico con canal perimetral
- **Apertura:** Gap lateral en el eje mayor

## 🖼️ Archivos Generados

- `brazalete_M_v1.step` - Formato CAD editable
- `brazalete_M_v1.stl` - Malla para impresión 3D
- `brazalete_M_v1.obj` - Formato Wavefront
- `brazalete_preview.png` - Vista previa 3D
- `brazalete_vista.png` - Múltiples ángulos
- `brazalete_vistas_2d.png` - Vistas técnicas 2D

## 📝 TODO / Pendientes

- [x] Script generador base
- [x] Visualizador matplotlib
- [ ] Ajustar parámetros del canal según feedback
- [ ] Generar todas las tallas (XS, S, L)
- [ ] Prueba de impresión 3D
- [ ] Iteración de diseño post-prueba

## 🔗 Enlaces

- **Entorno FreeCAD:** `~/projects/freecad-env/`
- **Documentación FreeCAD:** https://wiki.freecad.org

---
**Creado:** 2026-02-02  
**Última actualización:** 2026-02-02
