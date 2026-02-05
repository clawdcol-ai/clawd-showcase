#!/usr/bin/env python3
"""
step_to_stl.py - Convierte archivo STEP a STL usando FreeCAD
"""

import FreeCAD
import Part
import Mesh
import sys

def step_to_stl(archivo_step, archivo_stl=None):
    """Convierte un archivo STEP a STL usando FreeCAD"""
    
    if archivo_stl is None:
        archivo_stl = archivo_step.replace('.step', '.stl').replace('.STEP', '.stl')
    
    print(f"Cargando {archivo_step}...")
    
    # Importar el archivo STEP
    doc = FreeCAD.newDocument()
    Part.insert(archivo_step, doc.Name)
    
    # Obtener la forma (shape) del documento
    shape = None
    for obj in doc.Objects:
        if hasattr(obj, 'Shape'):
            shape = obj.Shape
            break
    
    if shape is None:
        print("Error: No se encontró forma en el archivo STEP")
        return False
    
    print(f"Forma cargada: {shape.Volume:.1f} mm³")
    
    # Crear malla desde la forma
    print("Creando malla...")
    mesh = Mesh.Mesh()
    mesh.addMesh(Mesh.Mesh(shape.tessellate(0.1)))  # 0.1mm de resolución
    
    # Exportar STL
    mesh.write(archivo_stl)
    print(f"✅ STL exportado: {archivo_stl}")
    print(f"   Vértices: {len(mesh.Points)}")
    print(f"   Caras: {len(mesh.Facets)}")
    
    return True

# Ejecutar siempre en FreeCAD
archivo = sys.argv[1] if len(sys.argv) > 1 else "Brazalete_Maverick_M.step"
step_to_stl(archivo)
