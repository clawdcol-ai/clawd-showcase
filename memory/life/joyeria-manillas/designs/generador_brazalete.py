#!/usr/bin/env python3
"""
generador_brazalete.py - Generador paramétrico de brazalete elíptico para pelo
Hair-Tie Hider Cuff - Tallas XS a L

Uso: python3 generador_brazalete.py [talla]
Ejemplo: python3 generador_brazalete.py M

Tallas disponibles: XS, S, M, L
"""

import sys
import math

# ============================================================
# CONFIGURACIÓN PARAMÉTRICA - MODIFICAR ESTAS VARIABLES
# ============================================================

# Tallas predefinidas (circunferencia interna en mm)
TALLAS = {
    'XS': {'circumference': 150, 'gap': 35, 'width': 8, 'thickness': 3},
    'S':  {'circumference': 160, 'gap': 36, 'width': 8, 'thickness': 3},
    'M':  {'circumference': 170, 'gap': 38, 'width': 8, 'thickness': 3},
    'L':  {'circumference': 180, 'gap': 40, 'width': 8, 'thickness': 3},
}

# Canal para la liga
CANAL_WIDTH = 4.0      # mm - ancho de la hendidura
CANAL_DEPTH = 1.5      # mm - profundidad de la hendidura

# ============================================================
# CÁLCULO DE ELIPSE - Aproximación de Ramanujan
# ============================================================

def calcular_semiejes_elipse(perimetro, ratio_elipse=1.15):
    """
    Calcula los semi-ejes 'a' y 'b' de una elipse dado su perímetro.
    Usa la aproximación de Ramanujan para el perímetro de elipse.
    
    Fórmula de Ramanujan (aproximación):
    P ≈ π * [3(a+b) - √((3a+b)(a+3b))]
    
    ratio_elipse: relación entre eje mayor y eje menor (a/b)
    """
    # Asumimos una relación de aspecto para la elipse
    # ratio_elipse = a / b
    
    # Iteramos para encontrar los valores correctos
    # Simplificación: usamos una aproximación numérica
    
    # Para una primera aproximación, tratamos como círculo
    radio_aprox = perimetro / (2 * math.pi)
    
    # Luego aplicamos el ratio de elipse
    b = radio_aprox / math.sqrt(ratio_elipse)  # semi-eje menor
    a = b * ratio_elipse  # semi-eje mayor
    
    # Verificamos con Ramanujan y ajustamos
    def perimetro_ramanujan(a, b):
        h = ((a - b) ** 2) / ((a + b) ** 2)
        return math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))
    
    # Ajuste iterativo simple
    for _ in range(10):
        p_calc = perimetro_ramanujan(a, b)
        factor = perimetro / p_calc
        a *= factor
        b = a / ratio_elipse
    
    return a, b

# ============================================================
# GENERACIÓN DEL BRAZALETE EN FREECAD
# ============================================================

def generar_brazalete(talla='M'):
    """Genera el brazalete para la talla especificada"""
    
    try:
        import Part
        import FreeCAD
        from FreeCAD import Base, Vector
    except ImportError:
        print("❌ Error: FreeCAD no está instalado o no se encuentra el módulo Part")
        print("   Asegúrate de tener FreeCAD instalado:")
        print("   - Ubuntu/Debian: sudo apt install freecad")
        print("   - O usa el AppImage de FreeCAD")
        sys.exit(1)
    
    # Obtener parámetros de la talla
    if talla not in TALLAS:
        print(f"❌ Talla '{talla}' no válida. Usa: {', '.join(TALLAS.keys())}")
        sys.exit(1)
    
    params = TALLAS[talla]
    C = params['circumference']  # Circunferencia interna
    G = params['gap']             # Opening gap
    W = params['width']           # Ancho del brazalete
    T = params['thickness']       # Grosor del material
    
    print(f"🏭 Generando brazalete talla {talla}...")
    print(f"   Circunferencia: {C}mm")
    print(f"   Gap: {G}mm")
    print(f"   Ancho: {W}mm")
    print(f"   Grosor: {T}mm")
    
    # Calcular semi-ejes de la elipse
    a, b = calcular_semiejes_elipse(C)
    print(f"   Semi-eje mayor (a): {a:.2f}mm")
    print(f"   Semi-eje menor (b): {b:.2f}mm")
    
    # Radio exterior (incluyendo grosor)
    a_outer = a + T
    b_outer = b + T
    
    # ========================================
    # 1. CREAR ELIPSE EXTERIOR (cilindro elíptico)
    # ========================================
    print("\n🔨 Creando forma exterior...")
    
    # Crear elipse exterior
    ellipse_outer = Part.Ellipse(Vector(0, 0, 0), a_outer, b_outer)
    edge_outer = Part.Edge(ellipse_outer)
    wire_outer = Part.Wire([edge_outer])
    face_outer = Part.Face(wire_outer)
    
    # Extruir para crear el cilindro
    solid_outer = face_outer.extrude(Vector(0, 0, W))
    
    # ========================================
    # 2. CREAR ELIPSE INTERIOR (para vaciar)
    # ========================================
    print("🔨 Creando cavidad interior...")
    
    ellipse_inner = Part.Ellipse(Vector(0, 0, -0.1), a, b)  # -0.1 para asegurar corte completo
    edge_inner = Part.Edge(ellipse_inner)
    wire_inner = Part.Wire([edge_inner])
    face_inner = Part.Face(wire_inner)
    
    # Extruir un poco más para asegurar el corte
    solid_inner = face_inner.extrude(Vector(0, 0, W + 0.2))
    
    # ========================================
    # 3. REALIZAR CORTE BOOLEANO (exterior - interior)
    # ========================================
    print("🔨 Realizando sustracción booleana...")
    
    brazalete_base = solid_outer.cut(solid_inner)
    
    # ========================================
    # 4. CREAR CANAL PARA LA LIGA
    # ========================================
    print("🔨 Creando canal para la liga...")
    
    # Posición del canal: centrado en el ancho, en la parte superior
    canal_z = W / 2
    canal_a = a_outer  # Radio exterior donde va el canal
    canal_b = b_outer
    
    # Crear el toroide elíptico para el canal
    # Usamos un barrido (sweep) de un círculo alrededor de la elipse
    
    # Radio del canal (semi-círculo)
    r_canal = CANAL_WIDTH / 2
    
    # Crear perfil del canal (círculo)
    canal_profile = Part.Circle(Vector(canal_a, 0, canal_z), Vector(1, 0, 0), r_canal)
    canal_edge = Part.Edge(canal_profile)
    canal_wire = Part.Wire([canal_edge])
    canal_face = Part.Face(canal_wire)
    
    # Trayectoria: elipse exterior
    path_ellipse = Part.Ellipse(Vector(0, 0, canal_z), canal_a, canal_b)
    path_edge = Part.Edge(path_ellipse)
    path_wire = Part.Wire([path_edge])
    
    # Realizar barrido (sweep)
    try:
        canal_solid = canal_face.makePipeShell([path_wire], True, True)
    except:
        # Si falla el sweep, usamos una aproximación con toroides
        print("   Usando método alternativo para el canal...")
        # Crear múltiples esferas a lo largo de la elipse
        canal_parts = []
        n_segments = 36
        for i in range(n_segments):
            angle = 2 * math.pi * i / n_segments
            x = canal_a * math.cos(angle)
            y = canal_b * math.sin(angle)
            
            # Esfera para cada segmento
            sphere = Part.makeSphere(r_canal, Vector(x, y, canal_z))
            canal_parts.append(sphere)
        
        # Fusionar todas las partes del canal
        canal_solid = canal_parts[0]
        for part in canal_parts[1:]:
            canal_solid = canal_solid.fuse(part)
    
    # ========================================
    # 5. CORTAR EL CANAL EN EL BRAZALETE
    # ========================================
    print("🔨 Integrando canal en el brazalete...")
    
    # El canal se resta del brazalete
    brazalete_con_canal = brazalete_base.cut(canal_solid)
    
    # ========================================
    # 6. CREAR EL "OPENING GAP" (apertura de 38mm)
    # ========================================
    print(f"🔨 Creando opening gap de {G}mm...")
    
    # Crear un bloque que corte la elipse
    # El bloque debe ser lo suficientemente grande
    block_size = max(a_outer, b_outer) * 3
    block_depth = W + 2
    
    # Posicionar el bloque para crear el gap
    # Lo colocamos en el eje X positivo
    gap_block = Part.makeBox(block_size, G, block_depth, 
                              Vector(0, -G/2, -0.5))
    
    # Realizar el corte
    brazalete_final = brazalete_con_canal.cut(gap_block)
    
    # ========================================
    # 7. REFINAR LA FORMA
    # ========================================
    print("🔨 Refinando geometría...")
    
    # Verificar validez (solo si el método existe)
    if hasattr(brazalete_final, 'isValid') and not brazalete_final.isValid():
        print("⚠️  Advertencia: La geometría puede tener problemas")
    
    # ========================================
    # 8. EXPORTAR
    # ========================================
    nombre_base = f"brazalete_{talla}_v1"
    
    # Exportar como STEP
    archivo_step = f"{nombre_base}.step"
    print(f"\n💾 Exportando {archivo_step}...")
    Part.export([brazalete_final], archivo_step)
    
    # Exportar como STL
    archivo_stl = f"{nombre_base}.stl"
    print(f"💾 Exportando {archivo_stl}...")
    
    # Para STL necesitamos mallas, convertimos la forma
    try:
        import Mesh
        mesh = Mesh.Mesh()
        mesh.addMesh(Mesh.Mesh(brazalete_final.tessellate(0.1)))
        mesh.write(archivo_stl)
    except ImportError:
        print("⚠️  Módulo Mesh no disponible, exportando solo STEP")
    
    print(f"\n✅ Brazalete talla {talla} generado exitosamente!")
    print(f"   Archivos: {archivo_step}, {archivo_stl}")
    
    return brazalete_final

# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    # Obtener talla de argumentos o usar M por defecto
    # Filtrar argumentos que empiezan con '--' (flags de FreeCAD)
    args_validos = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
    talla = args_validos[0] if args_validos else 'M'
    talla = talla.upper()
    
    print("=" * 60)
    print("🏭 GENERADOR DE BRAZALETE ELÍPTICO - Hair-Tie Hider Cuff")
    print("=" * 60)
    
    try:
        brazalete = generar_brazalete(talla)
    except Exception as e:
        print(f"\n❌ Error generando brazalete: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
