#!/usr/bin/env python3
"""
Script para verificar qué dispositivos de cámara están disponibles en el sistema.
Útil para diagnosticar problemas de cámara.
"""

import cv2
import glob
import os
import subprocess

def check_video_devices():
    """Verifica qué dispositivos de video están disponibles en el sistema"""
    print("Verificando dispositivos de video disponibles...")
    print()
    
    # Listar todos los dispositivos /dev/video*
    video_devices = glob.glob('/dev/video*')
    if not video_devices:
        print("No se encontraron dispositivos /dev/video*")
        return
    
    print(f"Dispositivos encontrados: {len(video_devices)}")
    for device in sorted(video_devices):
        print(f"  - {device}")
    print()
    
    # Verificar permisos
    print("Verificando permisos...")
    for device in video_devices:
        try:
            stat_info = os.stat(device)
            permissions = oct(stat_info.st_mode)[-3:]
            owner = stat_info.st_uid
            print(f"  {device}: permisos {permissions}, owner {owner}")
        except Exception as e:
            print(f"  {device}: error al verificar permisos - {e}")
    print()

def test_camera_devices():
    """Prueba cada dispositivo de cámara para ver cuáles funcionan"""
    print("Probando dispositivos de cámara...")
    print()
    
    # Probar dispositivos comunes primero
    common_devices = [0, 1, 2, 3]
    
    for device_index in common_devices:
        print(f"Probando /dev/video{device_index}...")
        
        try:
            cap = cv2.VideoCapture(device_index)
            
            if not cap.isOpened():
                print(f"  No se pudo abrir /dev/video{device_index}")
                continue
            
            # Obtener información de la cámara
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"  Dispositivo abierto correctamente")
            print(f"     Resolución: {width}x{height}")
            print(f"     FPS: {fps}")
            
            # Intentar leer un frame
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"   Frame capturado correctamente")
                print(f"     Tamaño del frame: {frame.shape}")
            else:
                print(f"   No se pudo capturar frame")
            
            cap.release()
            
        except Exception as e:
            print(f"   Error: {e}")
        
        print()

def check_camera_info():
    """Obtiene información adicional sobre las cámaras usando v4l2-ctl"""
    print("Información detallada de cámaras (v4l2-ctl)...")
    print()
    
    try:
        # Verificar si v4l2-ctl está disponible
        result = subprocess.run(['which', 'v4l2-ctl'], capture_output=True, text=True)
        if result.returncode != 0:
            print(" v4l2-ctl no está instalado. Instala con: sudo apt install v4l-utils")
            return
        
        # Listar dispositivos con v4l2-ctl
        result = subprocess.run(['v4l2-ctl', '--list-devices'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Dispositivos detectados por v4l2-ctl:")
            print(result.stdout)
        else:
            print("Error ejecutando v4l2-ctl --list-devices")
            
    except Exception as e:
        print(f"Error obteniendo información de v4l2-ctl: {e}")

def main():
    print("=" * 60)
    print("DIAGNÓSTICO DE CÁMARAS - SISTEMA DE DETECCIÓN DE FATIGA")
    print("=" * 60)
    print()
    
    check_video_devices()
    test_camera_devices()
    check_camera_info()
    
    print("=" * 60)
    print("SUGERENCIAS:")
    print("  - Si no hay dispositivos /dev/video*, verifica que la cámara esté conectada")
    print("  - Si hay dispositivos pero no funcionan, verifica los permisos")
    print("  - Para instalar v4l-utils: sudo apt install v4l-utils")
    print("  - Para dar permisos: sudo usermod -a -G video $USER")
    print("  - Reinicia la sesión después de cambiar permisos")
    print("=" * 60)

if __name__ == "__main__":
    main() 
