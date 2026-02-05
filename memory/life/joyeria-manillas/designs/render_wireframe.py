#!/usr/bin/env python3
"""
render_wireframe.py - Render wireframe rápido del brazalete
"""

import trimesh
import matplotlib.pyplot as plt
import numpy as np
import sys

def render_wireframe(archivo_stl, archivo_salida='brazalete_vista.png'):
    """Crea una visualización wireframe del STL"""
    
    print(f"📂 Cargando {archivo_stl}...")
    mesh = trimesh.load(archivo_stl)
    
    print(f"   {len(mesh.vertices):,} vértices, {len(mesh.faces):,} caras")
    
    # Crear figura
    fig = plt.figure(figsize=(14, 10))
    
    # Definir vistas
    vistas = [
        (30, 45, 'Isométrica'),
        (90, 0, 'Superior'),
        (0, 0, 'Frontal'),
        (0, 90, 'Lateral')
    ]
    
    for idx, (elev, azim, titulo) in enumerate(vistas, 1):
        ax = fig.add_subplot(2, 2, idx, projection='3d')
        
        # Mostrar solo algunas aristas para no saturar
        # Tomamos cada 50ª cara para el wireframe
        step = max(1, len(mesh.faces) // 500)
        faces_sample = mesh.faces[::step]
        
        for face in faces_sample:
            xs = mesh.vertices[face, 0]
            ys = mesh.vertices[face, 1]
            zs = mesh.vertices[face, 2]
            # Cerrar el triángulo
            xs = np.append(xs, xs[0])
            ys = np.append(ys, ys[0])
            zs = np.append(zs, zs[0])
            ax.plot(xs, ys, zs, 'b-', alpha=0.3, linewidth=0.5)
        
        # También mostrar algunos puntos de los vértices
        step_v = max(1, len(mesh.vertices) // 200)
        ax.scatter(mesh.vertices[::step_v, 0], 
                  mesh.vertices[::step_v, 1], 
                  mesh.vertices[::step_v, 2], 
                  c='red', s=1, alpha=0.5)
        
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
    
    plt.suptitle('Brazalete Elíptico - Hair-Tie Hider Cuff (Talla M)\n' + 
                 f'Dimensiones: {mesh.extents[0]:.1f} x {mesh.extents[1]:.1f} x {mesh.extents[2]:.1f} mm',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"\n💾 Imagen guardada: {archivo_salida}")
    
    # También crear una vista 2D simplificada (silueta)
    fig2, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Vista XY
    axes[0, 0].scatter(mesh.vertices[:, 0], mesh.vertices[:, 1], s=0.1, alpha=0.3)
    axes[0, 0].set_title('Vista Superior (XY)')
    axes[0, 0].set_xlabel('X (mm)')
    axes[0, 0].set_ylabel('Y (mm)')
    axes[0, 0].axis('equal')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Vista XZ
    axes[0, 1].scatter(mesh.vertices[:, 0], mesh.vertices[:, 2], s=0.1, alpha=0.3)
    axes[0, 1].set_title('Vista Frontal (XZ)')
    axes[0, 1].set_xlabel('X (mm)')
    axes[0, 1].set_ylabel('Z (mm)')
    axes[0, 1].axis('equal')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Vista YZ
    axes[1, 0].scatter(mesh.vertices[:, 1], mesh.vertices[:, 2], s=0.1, alpha=0.3)
    axes[1, 0].set_title('Vista Lateral (YZ)')
    axes[1, 0].set_xlabel('Y (mm)')
    axes[1, 0].set_ylabel('Z (mm)')
    axes[1, 0].axis('equal')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Histograma de alturas (Z)
    axes[1, 1].hist(mesh.vertices[:, 2], bins=50, color='steelblue', edgecolor='black')
    axes[1, 1].set_title('Distribución de alturas (Z)')
    axes[1, 1].set_xlabel('Z (mm)')
    axes[1, 1].set_ylabel('Frecuencia')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Vistas 2D - Brazalete Talla M', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('brazalete_vistas_2d.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"💾 Vistas 2D guardadas: brazalete_vistas_2d.png")

if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else 'brazalete_M_v1.stl'
    render_wireframe(archivo)
