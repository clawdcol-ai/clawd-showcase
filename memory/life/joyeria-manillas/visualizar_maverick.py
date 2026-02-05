"""
Visualizador 3D del Brazalete Maverick
Forma elíptica con canal para liga y gap de apertura
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# === CONFIGURACIÓN ===
TALLA = "M"
TALLAS = {
    "XS": {"circ": 135.0, "gap": 30.0},
    "S": {"circ": 145.0, "gap": 30.0},
    "SM": {"circ": 155.0, "gap": 33.0},
    "M": {"circ": 170.0, "gap": 38.0},
    "L": {"circ": 190.0, "gap": 40.0}
}

# Parámetros
datos = TALLAS[TALLA]
circ = datos["circ"]
gap = datos["gap"]
ancho_brazalete = 8.0
grosor_pared = 3.0
profundidad_canal = 1.2
ancho_canal = 4.0
ratio = 1.3  # Ancho/Alto de la muñeca

# Calcular radios de la elipse
b = circ / (2 * np.pi * np.sqrt((ratio**2 + 1) / 2))
a = b * ratio

radio_mayor_int = a
radio_menor_int = b
radio_mayor_ext = a + grosor_pared
radio_menor_ext = b + grosor_pared

print(f"Talla {TALLA}:")
print(f"  Circunferencia: {circ}mm")
print(f"  Radio Mayor (int): {radio_mayor_int:.2f}mm")
print(f"  Radio Menor (int): {radio_menor_int:.2f}mm")
print(f"  Grosor pared: {grosor_pared}mm")
print(f"  Gap apertura: {gap}mm")

fig = plt.figure(figsize=(14, 10))

# Vista 1: Perspectiva 3D
ax1 = fig.add_subplot(221, projection='3d')

# Crear malla para el brazalete (elipse toroidal con gap)
theta = np.linspace(0, 2*np.pi, 100)
phi = np.linspace(0, ancho_brazalete, 20)

# Ángulo del gap (cuánto quitamos del círculo)
theta_gap = np.arctan2(gap/2, radio_mayor_int) * 2
theta_inicio = -np.pi + theta_gap/2
theta_fin = np.pi - theta_gap/2
theta_cortado = np.linspace(theta_inicio, theta_fin, 80)

# Superficie exterior e interior con el canal
THETA, PHI = np.meshgrid(theta_cortado, phi)

# Radio variable según Z (para simular el canal)
def radio_con_canal(r_base, z, es_exterior=True):
    """Simula el canal en el centro del brazalete"""
    centro_canal = ancho_brazalete / 2
    medio_ancho = ancho_canal / 2
    
    # Si estamos en la zona del canal, reducimos el radio
    if es_exterior and abs(z - centro_canal) < medio_ancho:
        # Dentro del canal: radio menor
        return r_base - profundidad_canal * np.cos((z - centro_canal) / medio_ancho * np.pi/2)**2
    return r_base

# Puntos de la superficie exterior
X_ext = np.zeros_like(THETA)
Y_ext = np.zeros_like(THETA)
Z_ext = PHI

for i in range(len(phi)):
    for j in range(len(theta_cortado)):
        r_eff = radio_con_canal(radio_mayor_ext, phi[i], True)
        X_ext[i,j] = r_eff * np.cos(theta_cortado[j])
        Y_ext[i,j] = radio_menor_ext/radio_mayor_ext * r_eff * np.sin(theta_cortado[j])
        Z_ext[i,j] = phi[i]

# Puntos de la superficie interior
X_int = np.zeros_like(THETA)
Y_int = np.zeros_like(THETA)
Z_int = PHI

for i in range(len(phi)):
    for j in range(len(theta_cortado)):
        r_eff = radio_con_canal(radio_mayor_int, phi[i], False)
        X_int[i,j] = r_eff * np.cos(theta_cortado[j])
        Y_int[i,j] = radio_menor_int/radio_mayor_int * r_eff * np.sin(theta_cortado[j])
        Z_int[i,j] = phi[i]

# Dibujar superficies
ax1.plot_surface(X_ext, Y_ext, Z_ext, alpha=0.7, color='#C9A961', edgecolor='none')
ax1.plot_surface(X_int, Y_int, Z_int, alpha=0.7, color='#8B7355', edgecolor='none')

# Tapas del gap (para cerrar el modelo visualmente)
# Cara exterior del gap
gap_angle = theta_gap / 2
for signo in [-1, 1]:
    angle = np.pi * signo
    # Punto en el borde exterior
    x_ext = radio_mayor_ext * np.cos(angle)
    y_ext = radio_menor_ext * np.sin(angle)
    # Punto en el borde interior
    x_int = radio_mayor_int * np.cos(angle)
    y_int = radio_menor_int * np.sin(angle)
    
    # Dibujar la tapa
    for z in np.linspace(0, ancho_brazalete, 5):
        ax1.plot([x_int, x_ext], [y_int, y_ext], [z, z], 'k-', alpha=0.3, linewidth=0.5)

ax1.set_xlabel('X (mm)')
ax1.set_ylabel('Y (mm)')
ax1.set_zlabel('Z (mm)')
ax1.set_title(f'Brazalete Maverick - Talla {TALLA} (3D)')
ax1.set_box_aspect([1,1,0.3])

# Vista 2: Vista superior (plano XY)
ax2 = fig.add_subplot(222)
theta_full = np.linspace(0, 2*np.pi, 200)

# Dibujar elipses completas para referencia
x_ext_full = radio_mayor_ext * np.cos(theta_full)
y_ext_full = radio_menor_ext * np.sin(theta_full)
x_int_full = radio_mayor_int * np.cos(theta_full)
y_int_full = radio_menor_int * np.sin(theta_full)

ax2.fill(x_ext_full, y_ext_full, color='#C9A961', alpha=0.3, label='Exterior')
ax2.fill(x_int_full, y_int_full, color='white', alpha=1.0)
ax2.plot(x_ext_full, y_ext_full, 'b-', linewidth=2, label='Ext')
ax2.plot(x_int_full, y_int_full, 'r-', linewidth=2, label='Int')

# Resaltar el gap
gap_angle = np.arctan2(gap/2, radio_mayor_int)
ax2.axvline(x=radio_mayor_ext*np.cos(np.pi), color='green', linestyle='--', alpha=0.5, label='Gap')
ax2.axvline(x=radio_mayor_ext*np.cos(np.pi), ymin=0.4, ymax=0.6, color='green', linewidth=4)

ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.set_title('Vista Superior (Plano XY)')
ax2.axis('equal')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Vista 3: Corte lateral (plano XZ)
ax3 = fig.add_subplot(223)
z_vals = np.linspace(0, ancho_brazalete, 100)

# Perfil del canal
r_ext_perfil = [radio_con_canal(radio_mayor_ext, z, True) for z in z_vals]
r_int_perfil = [radio_mayor_int] * len(z_vals)  # Interior es plano

ax3.fill_betweenx(z_vals, r_int_perfil, r_ext_perfil, color='#C9A961', alpha=0.5)
ax3.plot(r_ext_perfil, z_vals, 'b-', linewidth=2, label='Exterior')
ax3.plot(r_int_perfil, z_vals, 'r-', linewidth=2, label='Interior')

# Marcar el canal
centro_canal = ancho_brazalete / 2
ax3.axhline(y=centro_canal - ancho_canal/2, color='orange', linestyle='--', alpha=0.5)
ax3.axhline(y=centro_canal + ancho_canal/2, color='orange', linestyle='--', alpha=0.5)
ax3.fill_between([radio_mayor_int, radio_mayor_ext], 
                 centro_canal - ancho_canal/2, 
                 centro_canal + ancho_canal/2,
                 color='orange', alpha=0.3, label='Canal')

ax3.set_xlabel('Radio (mm)')
ax3.set_ylabel('Z (altura)')
ax3.set_title('Corte Lateral (Plano XZ) - Perfil del Canal')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Vista 4: Vista frontal (plano YZ)
ax4 = fig.add_subplot(224)

# Elipse vista de frente (solo el contorno)
theta_face = np.linspace(0, 2*np.pi, 100)
y_face_ext = radio_menor_ext * np.sin(theta_face)
z_face_ext = ancho_brazalete/2 + (ancho_brazalete/2) * np.cos(theta_face) * 0.1  # Ligera perspectiva

y_face_int = radio_menor_int * np.sin(theta_face)
z_face_int = ancho_brazalete/2 + (ancho_brazalete/2) * np.cos(theta_face) * 0.1

ax4.fill(y_face_ext, z_face_ext, color='#C9A961', alpha=0.3)
ax4.fill(y_face_int, z_face_int, color='white', alpha=1.0)
ax4.plot(y_face_ext, z_face_ext, 'b-', linewidth=2)
ax4.plot(y_face_int, z_face_int, 'r-', linewidth=2)

# Mostrar dimensiones
ax4.text(0, ancho_brazalete + 1, f'Ancho: {ancho_brazalete}mm', ha='center', fontsize=9)
ax4.text(radio_menor_ext + 2, ancho_brazalete/2, f'Grosor: {grosor_pared}mm', ha='left', fontsize=9)

ax4.set_xlabel('Y (mm)')
ax4.set_ylabel('Z (mm)')
ax4.set_title('Vista Frontal (Plano YZ)')
ax4.axis('equal')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('brazalete_maverick_v2.png', dpi=150, bbox_inches='tight', facecolor='white')
print("\n✅ Imagen guardada: brazalete_maverick_v2.png")
plt.show()
