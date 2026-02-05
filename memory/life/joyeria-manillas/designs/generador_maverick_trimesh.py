#!/usr/bin/env python3
"""
generador_maverick_trimesh.py - Generador de Brazalete Maverick usando trimesh
Headless - sin operaciones booleanas (más estable)
"""

import trimesh
import numpy as np
import math

# === CONFIGURACIÓN MAVERICK ===
TALLAS = {
    "XS": {"circ": 135.0, "gap": 30.0},
    "S": {"circ": 145.0, "gap": 30.0},
    "SM": {"circ": 155.0, "gap": 33.0},
    "M": {"circ": 170.0, "gap": 38.0},
    "L": {"circ": 190.0, "gap": 40.0}
}

def calcular_radios_elipse(circunferencia):
    """Calcula semiejes de elipse con ratio 1.3:1"""
    ratio = 1.3
    b = circunferencia / (2 * math.pi * math.sqrt((ratio**2 + 1) / 2))
    a = b * ratio
    return a, b

def crear_brazalete_con_canal(talla="M"):
    """
    Crea el brazalete Maverick con el canal integrado en la geometría.
    No usa operaciones booleanas - más estable.
    """
    
    print(f"Generando brazalete Maverick talla {talla}...")
    
    datos = TALLAS.get(talla, TALLAS["M"])
    circ = datos["circ"]
    gap = datos["gap"]
    
    # Parámetros
    ancho = 8.0
    grosor = 3.0
    prof_canal = 1.2
    ancho_canal = 4.0
    
    # Radios
    a, b = calcular_radios_elipse(circ)
    a_ext_base = a + grosor
    b_ext_base = b + grosor
    
    print(f"  Radios: mayor={a:.2f}mm, menor={b:.2f}mm")
    print(f"  Exterior base: mayor={a_ext_base:.2f}mm, menor={b_ext_base:.2f}mm")
    
    # === CREAR BRAZALETE CON CANAL INTEGRADO ===
    # En lugar de restar el canal, lo modelamos variando el radio exterior
    # según la posición Z (más profundo en el centro del canal)
    
    n_segments = 64  # Segmentos alrededor del perímetro
    n_capas = 16     # Capas en Z para mejor resolución del canal
    
    theta = np.linspace(0, 2*np.pi, n_segments, endpoint=False)
    z_vals = np.linspace(0, ancho, n_capas)
    
    vertices = []
    faces = []
    
    # Para cada capa Z, calculamos el radio exterior (que varía para el canal)
    for z in z_vals:
        # Factor de profundidad del canal según Z
        # El canal está centrado en ancho/2 con ancho = ancho_canal
        centro_canal = ancho / 2
        dist_al_centro = abs(z - centro_canal)
        
        if dist_al_centro < ancho_canal / 2:
            # Dentro del canal: reducir radio exterior
            # Perfil semicircular del canal
            profundidad = prof_canal * math.cos(dist_al_centro / (ancho_canal/2) * math.pi/2)
        else:
            # Fuera del canal: radio normal
            profundidad = 0
        
        a_ext = a_ext_base - profundidad
        b_ext = b_ext_base - profundidad
        
        for t in theta:
            # Dirección normal
            nx = np.cos(t) / a_ext_base if profundidad == 0 else np.cos(t) / a
            ny = np.sin(t) / b_ext_base if profundidad == 0 else np.sin(t) / b
            norm = np.sqrt(nx**2 + ny**2)
            nx /= norm
            ny /= norm
            
            # Exterior (radio variable con el canal)
            x_e = a_ext * np.cos(t)
            y_e = b_ext * np.sin(t)
            vertices.append([x_e, y_e, z])
            
            # Interior (radio fijo)
            x_i = a * np.cos(t)
            y_i = b * np.sin(t)
            vertices.append([x_i, y_i, z])
    
    vertices = np.array(vertices)
    n = n_segments
    
    # Crear faces
    for capa in range(n_capas - 1):
        for i in range(n):
            i_next = (i + 1) % n
            base_actual = capa * n * 2 + i * 2
            base_next = capa * n * 2 + i_next * 2
            base_arriba = (capa + 1) * n * 2 + i * 2
            base_arriba_next = (capa + 1) * n * 2 + i_next * 2
            
            # Pared exterior (ext_actual, ext_next_arriba, ext_arriba)
            faces.append([base_actual, base_arriba_next, base_arriba])
            faces.append([base_actual, base_next, base_arriba_next])
            
            # Pared interior (int_actual, int_arriba, int_next_arriba)
            faces.append([base_actual + 1, base_arriba + 1, base_arriba_next + 1])
            faces.append([base_actual + 1, base_arriba_next + 1, base_next + 1])
    
    # Tapas superior e inferior
    base_inf = 0
    base_sup = (n_capas - 1) * n * 2
    
    for i in range(n):
        i_next = (i + 1) % n
        # Tapa inferior (exterior, interior_next, interior)
        faces.append([base_inf + i*2, base_inf + i_next*2 + 1, base_inf + i*2 + 1])
        faces.append([base_inf + i*2, base_inf + i_next*2, base_inf + i_next*2 + 1])
        
        # Tapa superior
        faces.append([base_sup + i*2, base_sup + i*2 + 1, base_sup + i_next*2 + 1])
        faces.append([base_sup + i*2, base_sup + i_next*2 + 1, base_sup + i_next*2])
    
    faces = np.array(faces)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    print(f"  Geometría base - Vértices: {len(mesh.vertices)}, Caras: {len(mesh.faces)}")
    
    # === CREAR GAP (APERTURA) ===
    print("  Creando gap de apertura...")
    
    # Encontrar vértices que están en la zona del gap
    # El gap está en el extremo positivo del eje X
    
    gap_ancho = gap
    gap_centro_x = a_ext_base  # Aproximadamente donde queremos el corte
    
    # Identificar vértices a eliminar (los que están dentro del gap)
    # El gap es una franja vertical en Y, desde cierto X hacia la derecha
    vertices_a_mantener = []
    vertice_map = {}  # Mapeo de índices antiguos a nuevos
    
    for i, v in enumerate(mesh.vertices):
        x, y, z = v
        # El gap está centrado en Y=0, desde X > (a_ext_base - 5) aprox
        # Y con ancho 'gap' en dirección Y
        
        if x > (a - 2) and abs(y) < gap_ancho / 2:
            # Dentro del gap - eliminar
            continue
        
        vertices_a_mantener.append(i)
        vertice_map[i] = len(vertices_a_mantener) - 1
    
    # Crear nueva malla sin los vértices del gap
    nuevos_vertices = mesh.vertices[vertices_a_mantener]
    
    # Filtrar faces - solo mantener las que no usan vértices eliminados
    nuevas_faces = []
    for f in mesh.faces:
        if f[0] in vertice_map and f[1] in vertice_map and f[2] in vertice_map:
            nuevas_faces.append([vertice_map[f[0]], vertice_map[f[1]], vertice_map[f[2]]])
    
    mesh = trimesh.Trimesh(vertices=nuevos_vertices, faces=np.array(nuevas_faces))
    
    print(f"  Tras gap - Vértices: {len(mesh.vertices)}, Caras: {len(mesh.faces)}")
    
    # === LIMPIAR MALLA ===
    print("  Limpiando malla...")
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    mesh.update_faces(mesh.nondegenerate_faces())
    
    # Rellenar huecos del gap
    mesh.fill_holes()
    mesh.fix_normals()
    
    print(f"  Final - Vértices: {len(mesh.vertices)}, Caras: {len(mesh.faces)}")
    
    return mesh

def main():
    import sys
    
    talla = "M"
    if len(sys.argv) > 1 and sys.argv[1] in TALLAS:
        talla = sys.argv[1]
    
    print("=" * 60)
    print(f"BRAZALETE MAVERICK - Generador Trimesh (Headless)")
    print("=" * 60)
    
    mesh = crear_brazalete_con_canal(talla)
    
    # Exportar
    nombre = f"Brazalete_Maverick_Talla_{talla}"
    
    # STL
    mesh.export(f"{nombre}.stl")
    print(f"\n✅ Exportado: {nombre}.stl")
    
    # Información
    print(f"\n📊 Estadísticas:")
    print(f"   Vértices: {len(mesh.vertices):,}")
    print(f"   Caras: {len(mesh.faces):,}")
    print(f"   Dimensiones: {mesh.extents[0]:.1f} x {mesh.extents[1]:.1f} x {mesh.extents[2]:.1f} mm")
    print(f"   Volumen: {mesh.volume:.1f} mm³")
    print(f"   Área: {mesh.area:.1f} mm²")
    
    # Generar imagen de preview
    print("\n🎨 Generando vista previa...")
    generar_preview(mesh, f"{nombre}_preview.png")
    
    return mesh

def generar_preview(mesh, archivo_salida):
    """Genera una imagen de preview de la malla"""
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=(14, 10))
        
        # Vistas
        vistas = [
            (30, 45, 'Isométrica'),
            (90, 0, 'Superior'),
            (0, 0, 'Frontal'),
            (0, 90, 'Lateral')
        ]
        
        for idx, (elev, azim, titulo) in enumerate(vistas, 1):
            ax = fig.add_subplot(2, 2, idx, projection='3d')
            
            # Muestra algunas caras (no todas para no saturar)
            step = max(1, len(mesh.faces) // 500)
            for face in mesh.faces[::step]:
                xs = mesh.vertices[face, 0]
                ys = mesh.vertices[face, 1]
                zs = mesh.vertices[face, 2]
                # Agregar primer punto al final para cerrar
                xs = np.append(xs, xs[0])
                ys = np.append(ys, ys[0])
                zs = np.append(zs, zs[0])
                ax.plot(xs, ys, zs, 'b-', alpha=0.3, linewidth=0.3)
            
            ax.view_init(elev=elev, azim=azim)
            ax.set_title(titulo, fontsize=12, fontweight='bold')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            
            # Igualar proporciones
            max_range = max(mesh.extents)
            mid = mesh.centroid
            ax.set_xlim(mid[0] - max_range/2, mid[0] + max_range/2)
            ax.set_ylim(mid[1] - max_range/2, mid[1] + max_range/2)
            ax.set_zlim(mid[2] - max_range/2, mid[2] + max_range/2)
        
        plt.suptitle(f'Brazalete Maverick - Talla M\n' + 
                     f'Dimensiones: {mesh.extents[0]:.1f} x {mesh.extents[1]:.1f} x {mesh.extents[2]:.1f} mm',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(archivo_salida, dpi=150, bbox_inches='tight', 
                    facecolor='white', edgecolor='none')
        print(f"   💾 Preview guardado: {archivo_salida}")
        
    except Exception as e:
        print(f"   ⚠️  No se pudo generar preview: {e}")

if __name__ == "__main__":
    main()
