print("[DEBUG] Cargando imports...")
import FreeCAD
import Part
import math
import sys
print("[DEBUG] Imports cargados")

# === CONFIGURACIÓN DE TALLAS (Basada en tu imagen 1) ===
# XS: 13-13.9cm | Gap 3.0cm
# S: 14-14.9cm | Gap 3.0cm
# SM: 15-15.9cm | Gap 3.3cm
# M: 16-18cm | Gap 3.8cm
# L: 18-20cm | Gap 4.0cm

TALLAS = {
    "XS": {"circ": 135.0, "gap": 30.0},
    "S": {"circ": 145.0, "gap": 30.0},
    "SM": {"circ": 155.0, "gap": 33.0},
    "M": {"circ": 170.0, "gap": 38.0},
    "L": {"circ": 190.0, "gap": 40.0}
}

# Talla por defecto
TALLA_ELEGIDA = "M"

def crear_elipse(a, b):
    """Crea una elipse con semiejes a y b"""
    elipse = Part.Ellipse()
    elipse.MajorRadius = a
    elipse.MinorRadius = b
    return elipse

def generar_brazalete():
    print("[DEBUG] Entrando a generar_brazalete()")
    print(f"--- Generando Brazalete Maverick Talla {TALLA_ELEGIDA} ---")
    
    datos = TALLAS[TALLA_ELEGIDA]
    circ = datos["circ"]
    gap = datos["gap"]
    
    # Parámetros físicos
    ancho = 8.0           # Altura del brazalete
    grosor = 3.0          # Grosor de la pared de acero
    prof_canal = 1.2      # Profundidad del surco
    ancho_canal = 4.0     # Ancho del surco (para la liga)
    
    # MATEMÁTICA: De Circunferencia a Elipse
    # Usamos ratio 1.3 (la muñeca es ovalada)
    ratio = 1.3
    
    # Fórmula aproximada inversa de Ramanujan para hallar el radio menor (b)
    # Perimetro ≈ 2 * pi * sqrt((a^2 + b^2) / 2)
    b = circ / (2 * math.pi * math.sqrt((ratio**2 + 1) / 2))
    a = b * ratio
    
    print(f"Dimensiones calculadas: Eje Mayor {a*2:.1f}mm, Eje Menor {b*2:.1f}mm")
    
    # 1. CREAR EL TUBO BASE
    # Elipse externa
    elipse_ext = crear_elipse(a + grosor, b + grosor)
    edge_ext = Part.Edge(elipse_ext)
    wire_ext = Part.Wire([edge_ext])
    cara_ext = Part.Face(wire_ext)
    solido_ext = cara_ext.extrude(FreeCAD.Vector(0, 0, ancho))
    
    # Elipse interna (el hueco del brazo)
    elipse_int = crear_elipse(a, b)
    edge_int = Part.Edge(elipse_int)
    wire_int = Part.Wire([edge_int])
    cara_int = Part.Face(wire_int)
    solido_int = cara_int.extrude(FreeCAD.Vector(0, 0, ancho))
    
    cuerpo = solido_ext.cut(solido_int)
    
    # 2. TALLAR EL CANAL (GROOVE)
    # Creamos un anillo "negativo" para restar material
    pos_z = (ancho - ancho_canal) / 2
    
    # El anillo de corte debe ser un poco más grande que el externo para asegurar corte
    corte_int = crear_elipse(a + grosor - prof_canal, b + grosor - prof_canal)
    edge_c_int = Part.Edge(corte_int)
    wire_c_int = Part.Wire([edge_c_int])
    f_c_int = Part.Face(wire_c_int)
    
    corte_ext = crear_elipse(a + grosor + 5, b + grosor + 5)
    edge_c_ext = Part.Edge(corte_ext)
    wire_c_ext = Part.Wire([edge_c_ext])
    f_c_ext = Part.Face(wire_c_ext)
    
    s_c_int = f_c_int.extrude(FreeCAD.Vector(0, 0, ancho_canal))
    s_c_ext = f_c_ext.extrude(FreeCAD.Vector(0, 0, ancho_canal))
    
    anillo_corte = s_c_ext.cut(s_c_int)
    cuerpo = cuerpo.cut(anillo_corte)
    
    # 3. EL CORTE DE APERTURA (GAP)
    # Creamos una caja ("Cubo de Dios") para eliminar el segmento de entrada
    # Alineamos la caja al eje X positivo (derecha)
    box = Part.makeBox(50, gap, 20)  # Largo exagerado, Ancho exacto gap, Alto exagerado
    
    # Centramos la caja en Y (mitad arriba, mitad abajo)
    box.translate(FreeCAD.Vector(a - 5, -gap/2, -5))
    
    cuerpo = cuerpo.cut(box)
    
    # 4. REDONDEO (FILLET) - Intento seguro
    try:
        # Redondeamos bordes verticales del corte (para no cortar la piel)
        cuerpo = cuerpo.makeFillet(0.5, cuerpo.Edges)
    except:
        print("Aviso: No se pudo aplicar redondeo automático, entregando modelo bruto.")
    
    # 5. EXPORTAR
    nombre = f"Brazalete_Maverick_{TALLA_ELEGIDA}"
    Part.export([cuerpo], f"{nombre}.step")
    Part.export([cuerpo], f"{nombre}.stl")
    
    print(f"✅ ÉXITO TOTAL: Archivos guardados como {nombre}.step y .stl")

# Ejecutar siempre en FreeCAD (el nombre del módulo es el nombre del archivo)
generar_brazalete()
