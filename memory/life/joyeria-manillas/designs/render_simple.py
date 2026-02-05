#!/usr/bin/env python3
"""
render_simple.py - Render simple del brazalete usando trimesh scene
"""

import trimesh
import sys

def render_stl(archivo_stl):
    """Carga y muestra información del STL, intenta crear imagen"""
    
    print(f"📂 Analizando {archivo_stl}...\n")
    
    # Cargar la malla
    mesh = trimesh.load(archivo_stl)
    
    print("📊 ESTADÍSTICAS DEL MODELO:")
    print("=" * 40)
    print(f"   Vértices: {len(mesh.vertices):,}")
    print(f"   Caras (triángulos): {len(mesh.faces):,}")
    print(f"   Dimensiones (mm):")
    print(f"      X: {mesh.extents[0]:.2f}")
    print(f"      Y: {mesh.extents[1]:.2f}")
    print(f"      Z: {mesh.extents[2]:.2f}")
    print(f"   Volumen: {mesh.volume:.2f} mm³")
    print(f"   Área superficial: {mesh.area:.2f} mm²")
    
    print("\n🔍 BOUNDING BOX:")
    print("=" * 40)
    print(f"   Mín: ({mesh.bounds[0][0]:.2f}, {mesh.bounds[0][1]:.2f}, {mesh.bounds[0][2]:.2f})")
    print(f"   Máx: ({mesh.bounds[1][0]:.2f}, {mesh.bounds[1][1]:.2f}, {mesh.bounds[1][2]:.2f})")
    
    # Intentar exportar una imagen usando trimesh
    print("\n🎨 GENERANDO VISTA PREVIA...")
    
    try:
        # Crear una escena con iluminación
        mesh.visual.face_colors = [100, 150, 200, 255]  # Color azul claro
        
        scene = mesh.scene()
        
        # Guardar imagen desde diferentes ángulos
        angles = [
            (0, 0, 'frontal'),
            (0, 90, 'lateral'),
            (90, 0, 'superior'),
            (45, 45, 'isometrica')
        ]
        
        for elev, azim, nombre in angles:
            try:
                png = scene.save_image(
                    resolution=(800, 800),
                    angle=[elev, azim]
                )
                with open(f'brazalete_{nombre}.png', 'wb') as f:
                    f.write(png)
                print(f"   ✅ brazalete_{nombre}.png guardada")
            except Exception as e:
                print(f"   ⚠️  No se pudo guardar vista {nombre}: {e}")
                
    except Exception as e:
        print(f"   ⚠️  Error en renderizado: {e}")
        print("   (Esto es normal en modo headless sin display)")
    
    print("\n✅ Análisis completado")
    
    # Exportar un OBJ también (más ligero para visualizar)
    print("\n💾 Exportando a formato OBJ...")
    mesh.export('brazalete_M_v1.obj')
    print("   ✅ brazalete_M_v1.obj guardado")

if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else 'brazalete_M_v1.stl'
    render_stl(archivo)
