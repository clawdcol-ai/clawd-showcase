#!/usr/bin/env python3
"""
generador_brazalete_maverick.py - Script corregido para Brazalete Maverick
Hair-Tie Hider Cuff con canal para liga
"""

import FreeCAD
import Part
import math
import sys

# === CONFIGURACIÓN MAVERICK ===
TALLA_OBJETIVO = "M"

# Base de datos de Tallas (Circunferencia en mm, Gap en mm)
TALLAS = {
    "XS": {"circ": 135.0, "gap": 30.0},
    "S": {"circ": 145.0, "gap": 30.0},
    "SM": {"circ": 155.0, "gap": 33.0},
    "M": {"circ": 170.0, "gap": 38.0},
    "L": {"circ": 190.0, "gap": 40.0}
}

def calcular_radios_elipse(circunferencia):
    """
    Calcula los radios (semiejes) de una elipse basándose en su perímetro.
    Asumimos una proporción de muñeca humana estándar (ancho/alto ≈ 1.3)
    """
    ratio = 1.3
    # Perimetro = 2 * pi * sqrt((a^2 + b^2) / 2) -> despejando b
    b = circunferencia / (2 * math.pi * math.sqrt((ratio**2 + 1) / 2))
    a = b * ratio
    return a, b

def generar_brazalete(talla):
    print(f"--- Iniciando Protocolo Maverick para Talla {talla} ---")
    
    datos = TALLAS.get(talla)
    if not datos:
        print(f"Error: Talla {talla} no encontrada.")
        return
    
    circ = datos["circ"]
    gap = datos["gap"]
    
    # Parámetros fijos del diseño
    ancho_brazalete = 8.0
    grosor_pared = 3.0
    profundidad_canal = 1.2
    ancho_canal = 4.0
    
    # Calcular Geometría Base (Elipses)
    radio_mayor_int, radio_menor_int = calcular_radios_elipse(circ)
    radio_mayor_ext = radio_mayor_int + grosor_pared
    radio_menor_ext = radio_menor_int + grosor_pared
    
    print(f"Geometría: Radios Internos ({radio_mayor_int:.2f}, {radio_menor_int:.2f})")
    
    # Crear Sólido Base (Extrusión)
    # Elipse Exterior
    elipse_ext = Part.makeEllipse(radio_mayor_ext, radio_menor_ext, FreeCAD.Vector(0,0,0))
    cara_ext = Part.Face(Part.Wire(elipse_ext))
    solido_ext = cara_ext.extrude(FreeCAD.Vector(0, 0, ancho_brazalete))
    
    # Elipse Interior (El Vaciado)
    elipse_int = Part.makeEllipse(radio_mayor_int, radio_menor_int, FreeCAD.Vector(0,0,0))
    cara_int = Part.Face(Part.Wire(elipse_int))
    solido_int = cara_int.extrude(FreeCAD.Vector(0, 0, ancho_brazalete))
    
    # Realizar el corte principal (Tubo)
    cuerpo_base = solido_ext.cut(solido_int)
    
    # Crear el Canal para la Liga (The Groove)
    pos_z_canal = (ancho_brazalete - ancho_canal) / 2
    
    # Corrección: radios del cortador del canal
    elipse_canal_int = Part.makeEllipse(
        radio_mayor_ext - profundidad_canal,
        radio_menor_ext - profundidad_canal,
        FreeCAD.Vector(0,0,pos_z_canal)
    )
    elipse_canal_ext = Part.makeEllipse(
        radio_mayor_ext + 5,
        radio_menor_ext + 5,
        FreeCAD.Vector(0,0,pos_z_canal)
    )
    
    face_c_int = Part.Face(Part.Wire(elipse_canal_int))
    face_c_ext = Part.Face(Part.Wire(elipse_canal_ext))
    
    solido_c_int = face_c_int.extrude(FreeCAD.Vector(0,0,ancho_canal))
    solido_c_ext = face_c_ext.extrude(FreeCAD.Vector(0,0,ancho_canal))
    
    cortador_canal = solido_c_ext.cut(solido_c_int)
    cuerpo_con_canal = cuerpo_base.cut(cortador_canal)
    
    # Opening Gap (Corte lateral)
    box_gap = Part.makeBox(radio_mayor_ext * 2, gap, ancho_brazalete * 2)
    # Centrar en Y
    box_gap.translate(FreeCAD.Vector(0, -gap/2, -1))
    # Mover al extremo derecho
    box_gap.translate(FreeCAD.Vector(radio_mayor_int - 2, 0, 0))
    
    brazalete_final = cuerpo_con_canal.cut(box_gap)
    
    # Fillet (Redondeo) - Intentar suavizar bordes
    try:
        brazalete_final = brazalete_final.makeFillet(0.4, brazalete_final.Edges)
        print("Redondeo aplicado con éxito.")
    except:
        print("Advertencia: No se pudo aplicar redondeo automático.")
    
    # Exportar
    nombre_archivo = f"Brazalete_Maverick_Talla_{talla}"
    Part.export([brazalete_final], f"{nombre_archivo}.step")
    Part.export([brazalete_final], f"{nombre_archivo}.stl")
    
    print(f"✅ ÉXITO: Archivos generados: {nombre_archivo}.step y .stl")

if __name__ == "__main__":
    # Si pasas un argumento (ej: python script.py L), usa esa talla
    talla_a_usar = TALLA_OBJETIVO
    if len(sys.argv) > 1:
        if sys.argv[1] in TALLAS:
            talla_a_usar = sys.argv[1]
    
    generar_brazalete(talla_a_usar)
