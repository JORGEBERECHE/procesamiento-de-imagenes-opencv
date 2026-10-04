import cv2
import os
import threading
import time
from datetime import datetime
import numpy as np

FUENTE_VIDEO = 0  # 0 activa la cámara web integrada de la laptop

# Carpeta principal de almacenamiento
CARPETA_RAIZ = "fotogramas_laptop"

# Frecuencia de guardado en segundos (ejemplo: 1.0 = un fotograma por segundo)
INTERVALO_GUARDADO = 1.0  


class CapturaLaptop:
    def __init__(self, fuente):
        self.cap = cv2.VideoCapture(fuente)
        
        # Configurar resolución recomendada para webcams (1280x720)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.ret, self.frame = self.cap.read()
        self.corriendo = True
        
        # Hilo independiente para que la ventana de video no se congele al guardar imágenes
        self.hilo = threading.Thread(target=self._actualizar_camara, daemon=True)
        self.hilo.start()

    def _actualizar_camara(self):
        while self.corriendo:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.ret = ret
                    self.frame = frame
                else:
                    time.sleep(0.01)

    def obtener_frame(self):
        return self.ret, self.frame

    def liberar(self):
        self.corriendo = False
        self.hilo.join()
        self.cap.release()


def crear_estructura_directorios(raiz):
    """Organiza las carpetas automáticamente por Año-Mes-Día"""
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    ruta_destino = os.path.join(raiz, fecha_hoy)
    os.makedirs(ruta_destino, exist_ok=True)
    return ruta_destino


def iniciar_sistema():
    print("[INFO] Encendiendo la cámara de la laptop...")
    camara = CapturaLaptop(FUENTE_VIDEO)
    
    # Esperar un momento a que la cámara se estabilice (ajuste de luces automático)
    time.sleep(1.5)
    
    ultimo_guardado = time.time()
    print("[INFO] Sistema activo.")
    print("[REGLA] Presiona la tecla 'q' dentro de la ventana de video para cerrar de forma segura.")
    
    try:
        while True:
            ret, frame = camara.obtener_frame()
            
            if not ret or frame is None:
                print("[ALERTA] No se detecta imagen de la laptop. Esperando...")
                time.sleep(0.5)
                continue

            # Clonamos el frame para mostrar en pantalla sin retrasar el guardado
            vista_en_vivo = frame.copy()
            cv2.imshow("Camara de Laptop - Presiona 'q' para salir", vista_en_vivo)

            # Control de tiempo para guardado estructurado
            tiempo_actual = time.time()
            if tiempo_actual - ultimo_guardado >= INTERVALO_GUARDADO:
                carpeta_del_dia = crear_estructura_directorios(CARPETA_RAIZ)
                
                # Nombre de archivo estructurado: Hora-Minuto-Segundo-Milisegundo
                nombre_archivo = datetime.now().strftime("%H-%M-%S-%f")[:-3] + ".jpg"
                ruta_completa = os.path.join(carpeta_del_dia, nombre_archivo)
                
                # Guardar foto en el disco duro
                cv2.imwrite(ruta_completa, frame)
                ultimo_guardado = tiempo_actual

            # Capturar la tecla 'q' para cerrar el bucle
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n[INFO] Monitoreo detenido por teclado.")
        
    finally:
        print("[INFO] Apagando cámara y limpiando recursos...")
        camara.liberar()
        cv2.destroyAllWindows()
        print("[INFO] Ejecución finalizada con éxito.")


if __name__ == "__main__":
    iniciar_sistema()