#!/usr/bin/env python3
"""
visualizar_brazalete.py - Genera una imagen del STL usando matplotlib
"""

import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sys

def visualizar_stl(archivo_stl, archivo_salida='brazalete_preview.png'):
    """Carga un STL y genera una imagen de vista previa"""
    
    print(f"📂 Cargando {archivo_stl}...")
    
    # Cargar la malla
    mesh = trimesh.load(archivo_stl)
    
    print(f"   Vértices: {len(mesh.vertices)}")
    print(f"   Caras: {len(mesh.faces)}")
    print(f"   Dimensiones: {mesh.extents}")
    
    # Crear figura con múltiples vistas
    fig = plt.figure(figsize=(16, 12))
    
    # Vista 1: Perspectiva isométrica
    ax1 = fig.add_subplot(221, projection='3d')
    plot_mesh(ax1, mesh, 'Vista Isométrica', elev=30, azim=45)
    
    # Vista 2: Vista superior
    ax2 = fig.add_subplot(222, projection='3d')
    plot_mesh(ax2, mesh, 'Vista Superior', elev=90, azim=-90)
    
    # Vista 3: Vista frontal
    ax3 = fig.add_subplot(223, projection='3d')
    plot_mesh(ax3, mesh, 'Vista Frontal', elev=0, azim=-90)
    
    # Vista 4: Vista lateral
    ax4 = fig.add_subplot(224, projection='3d')
    plot_mesh(ax4, mesh, 'Vista Lateral', elev=0, azim=0)
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"\n💾 Imagen guardada: {archivo_salida}")
    
    # También crear una vista única grande
    fig2 = plt.figure(figsize=(10, 10))
    ax = fig2.add_subplot(111, projection='3d')
    plot_mesh(ax, mesh, 'Brazalete Elíptico - Hair-Tie Hider Cuff', 
              elev=35, azim=45, single=True)
    plt.tight_layout()
    plt.savefig('brazalete_single.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"💾 Imagen individual guardada: brazalete_single.png")

def plot_mesh(ax, mesh, title, elev, azim, single=False):
    """Dibuja la malla en los ejes dados"""
    
    # Obtener los vértices de las caras
    x = mesh.vertices[:, 0]
    y = mesh.vertices[:, 1]
    z = mesh.vertices[:, 2]
    
    # Dibujar la superficie
    ax.plot_trisurf(x, y, z, triangles=mesh.faces, 
                    cmap='viridis', alpha=0.9, 
                    edgecolor='none', antialiased=True)
    
    # Configurar vista
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    if single:
        ax.set_xlabel('X (mm)', fontsize=12)
        ax.set_ylabel('Y (mm)', fontsize=12)
        ax.set_zlabel('Z (mm)', fontsize=12)
    else:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
    
    # Igualar proporciones
    max_range = max(mesh.extents)
    mid_x = (mesh.bounds[0][0] + mesh.bounds[1][0]) / 2
    mid_y = (mesh.bounds[0][1] + mesh.bounds[1][1]) / 2
    mid_z = (mesh.bounds[0][2] + mesh.bounds[1][2]) / 2
    
    ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
    ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
    ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)

if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else 'brazalete_M_v1.stl'
    visualizar_stl(archivo)
