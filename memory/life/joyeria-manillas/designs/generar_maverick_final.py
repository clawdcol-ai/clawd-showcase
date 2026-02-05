#!/usr/bin/env python3
"""
generar_maverick_final.py - Genera el brazalete Maverick completo usando trimesh
Este script usa la misma lógica que maverick_real.py pero con trimesh para STL
"""

import trimesh
import numpy as np
import math

# === CONFIGURACIÓN ===
TALLAS = {
    "XS": {"circ": 135.0, "gap": 30.0},
    "S": {"circ": 145.0, "gap": 30.0},
    "SM": {"circ": 155.0, "gap": 33.0},
    "M": {"circ": 170.0, "gap": 38.0},
    "L": {"circ": 190.0, "gap": 40.0}
}

def calcular_elipse(circ, ratio=1.3):
    """Calcula semiejes de elipse"""
    b = circ / (2 * math.pi * math.sqrt((ratio**2 + 1) / 2))
    a = b * ratio
    return a, b

def crear_brazalete(talla="M"):
    print(f"--- Generando Brazalete Maverick Talla {talla} ---")
    
    datos = TALLAS[talla]
    circ = datos["circ"]
    gap = datos["gap"]
    
    # Parámetros
    ancho = 8.0
    grosor = 3.0
    prof_canal = 1.2
    ancho_canal = 4.0
    
    # Radios elipse
    a, b = calcular_elipse(circ)
    print(f"Dimensiones: Eje Mayor {a*2:.1f}mm, Eje Menor {b*2:.1f}mm")
    
    # === 1. TUBO BASE CON CANAL INTEGRADO ===
    n_segments = 80
    n_capas = 20
    theta = np.linspace(0, 2*np.pi, n_segments, endpoint=False)
    z_vals = np.linspace(0, ancho, n_capas)
    
    vertices = []
    faces = []
    
    for z in z_vals:
        # Perfil del canal: reducir radio en el centro
        centro_canal = ancho / 2
        dist = abs(z - centro_canal)
        
        if dist < ancho_canal / 2:
            # Dentro del canal
            prof = prof_canal * math.cos(dist / (ancho_canal/2) * math.pi/2)
        else:
            prof = 0
        
        a_ext = a + grosor - prof
        b_ext = b + grosor - prof
        
        for t in theta:
            # Normal
            nx = np.cos(t) / (a + grosor)
            ny = np.sin(t) / (b + grosor)
            norm = np.sqrt(nx**2 + ny**2)
            nx /= norm
            ny /= norm
            
            # Exterior
            x_e = a_ext * np.cos(t)
            y_e = b_ext * np.sin(t)
            vertices.append([x_e, y_e, z])
            
            # Interior
            x_i = a * np.cos(t)
            y_i = b * np.sin(t)
            vertices.append([x_i, y_i, z])
    
    vertices = np.array(vertices)
    n = n_segments
    
    # Faces
    for capa in range(n_capas - 1):
        for i in range(n):
            i_next = (i + 1) % n
            base = capa * n * 2 + i * 2
            base_next = capa * n * 2 + i_next * 2
            base_arriba = (capa + 1) * n * 2 + i * 2
            base_arriba_next = (capa + 1) * n * 2 + i_next * 2
            
            faces.append([base, base_arriba_next, base_arriba])
            faces.append([base, base_next, base_arriba_next])
            faces.append([base + 1, base_arriba + 1, base_arriba_next + 1])
            faces.append([base + 1, base_arriba_next + 1, base_next + 1])
    
    # Tapas
    base_inf = 0
    base_sup = (n_capas - 1) * n * 2
    for i in range(n):
        i_next = (i + 1) % n
        faces.append([base_inf + i*2, base_inf + i_next*2 + 1, base_inf + i*2 + 1])
        faces.append([base_inf + i*2, base_inf + i_next*2, base_inf + i_next*2 + 1])
        faces.append([base_sup + i*2, base_sup + i*2 + 1, base_sup + i_next*2 + 1])
        faces.append([base_sup + i*2, base_sup + i_next*2 + 1, base_sup + i_next*2])
    
    mesh = trimesh.Trimesh(vertices=vertices, faces=np.array(faces))
    
    # === 2. CORTAR EL GAP ===
    # Eliminar vértices dentro de la zona del gap
    vertices_a_mantener = []
    vertice_map = {}
    
    for i, v in enumerate(mesh.vertices):
        x, y, z = v
        # El gap está en X > a (extremo derecho) y |Y| < gap/2
        if x > (a - 2) and abs(y) < gap / 2:
            continue  # Eliminar
        vertices_a_mantener.append(i)
        vertice_map[i] = len(vertices_a_mantener) - 1
    
    nuevos_vertices = mesh.vertices[vertices_a_mantener]
    nuevas_faces = []
    for f in mesh.faces:
        if all(idx in vertice_map for idx in f):
            nuevas_faces.append([vertice_map[f[0]], vertice_map[f[1]], vertice_map[f[2]]])
    
    mesh = trimesh.Trimesh(vertices=nuevos_vertices, faces=np.array(nuevas_faces))
    
    # Limpiar
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.fill_holes()
    mesh.fix_normals()
    
    return mesh

def main():
    import sys
    talla = sys.argv[1] if len(sys.argv) > 1 else "M"
    
    mesh = crear_brazalete(talla)
    
    # Exportar
    nombre = f"Brazalete_Maverick_{talla}"
    mesh.export(f"{nombre}.stl")
    
    print(f"\n✅ ÉXITO: {nombre}.stl generado")
    print(f"   Vértices: {len(mesh.vertices):,}")
    print(f"   Caras: {len(mesh.faces):,}")
    print(f"   Volumen: {mesh.volume:.1f} mm³")
    print(f"   Dimensiones: {mesh.extents[0]:.1f} x {mesh.extents[1]:.1f} x {mesh.extents[2]:.1f} mm")

if __name__ == "__main__":
    main()
