#!/usr/bin/env python3
import cv2
import base64
import asyncio
import websockets
import json
import time
import numpy as np
from datetime import datetime
import os
import glob

def find_available_camera():
    """
    Detecta automáticamente qué dispositivo de cámara está disponible.
    Retorna el índice del primer dispositivo de cámara que funcione.
    """
    print("Detectando cámara disponible...")
    
    # Primero intenta con los dispositivos más comunes
    common_devices = [0, 1, 2, 3]
    
    for device_index in common_devices:
        print(f"  Probando /dev/video{device_index}...")
        cap = cv2.VideoCapture(device_index)
        if cap.isOpened():
            # Intenta leer un frame para verificar que realmente funciona
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None:
                print(f"Cámara encontrada en /dev/video{device_index}")
                return device_index
            else:
                print(f"   /dev/video{device_index} no puede leer frames")
        else:
            print(f"   /dev/video{device_index} no está disponible")
    
    # Si no encuentra nada en los dispositivos comunes, busca todos los dispositivos video
    print("  Buscando otros dispositivos de video...")
    video_devices = glob.glob('/dev/video*')
    for device_path in video_devices:
        try:
            device_index = int(device_path.split('/dev/video')[1])
            print(f"  Probando {device_path}...")
            cap = cv2.VideoCapture(device_index)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    print(f"Cámara encontrada en {device_path}")
                    return device_index
        except (ValueError, IndexError):
            continue
    
    print("No se encontró ninguna cámara disponible")
    return None

class CameraFatigueDetector:
    def __init__(self, camera_device=None, websocket_url="ws://localhost:8000/ws"):
        # Si no se especifica camera_device, detecta automáticamente
        if camera_device is None:
            self.camera_device = find_available_camera()
            if self.camera_device is None:
                raise RuntimeError("No se pudo encontrar ninguna cámara disponible")
        else:
            self.camera_device = camera_device
        
        self.websocket_url = websocket_url
        self.websocket = None
        self.is_running = False
        print(f"Usando cámara en /dev/video{self.camera_device}")

    async def connect_websocket(self):
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            print(f"Conectado al servidor de detección de fatiga en {self.websocket_url}")
            return True
        except Exception as e:
            print(f"Error conectando al WebSocket: {e}")
            return False

    def capture_single_frame(self):
        try:
            cap = cv2.VideoCapture(self.camera_device)
            if not cap.isOpened():
                print(f"Error: No se pudo abrir la cámara en /dev/video{self.camera_device}")
                return None
            
            # Configurar propiedades de la cámara
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Esperar un poco para que la cámara se estabilice
            time.sleep(0.2)
            
            # Intentar leer el frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                print(f"Error: No se pudo capturar frame de /dev/video{self.camera_device}")
                return None
            
            # Verificar que el frame tiene contenido válido
            if frame.size == 0:
                print(f"Error: Frame vacío de /dev/video{self.camera_device}")
                return None
            
            return frame
            
        except Exception as e:
            print(f"Error capturando frame: {e}")
            return None

    def frame_to_base64(self, frame):
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            base64_string = base64.b64encode(buffer).decode('utf-8')
            return base64_string
        except Exception as e:
            print(f"Error convirtiendo frame a base64: {e}")
            return None

    async def send_frame_to_server(self, base64_frame):
        if not self.websocket:
            return None
        try:
            await self.websocket.send(base64_frame)
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            print(f"Error enviando frame al servidor: {e}")
            return None

    def save_frame_for_display(self, frame, filename="current_frame.jpg"):
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            static_dir = os.path.join(script_dir, "static")
            
            # Ensure static directory exists
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)
                print(f"Created static directory: {static_dir}")
            
            # Save the image
            image_path = os.path.join(static_dir, filename)
            success = cv2.imwrite(image_path, frame)
            if success:
                print(f"Frame saved successfully to: {image_path}")
            else:
                print(f"Failed to save frame to: {image_path}")
            return success
        except Exception as e:
            print(f"Error guardando frame: {e}")
            return False

    async def process_fatigue_detection(self, fatigue_data):
        if not fatigue_data:
            return
        try:
            import requests
            response = requests.post(
                'http://localhost:5000/api/fatigue/data',
                json=fatigue_data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"Fatigue level: {result.get('fatigue_level', 'Unknown')}")
            else:
                print(f"Error enviando datos a Flask: {response.status_code}")
        except Exception as e:
            print(f"Error procesando detección de fatiga: {e}")

    async def run_detection_loop(self):
        print("Iniciando bucle de detección de fatiga...")
        self.is_running = True
        while self.is_running:
            try:
                frame = self.capture_single_frame()
                if frame is None:
                    print("No se pudo capturar frame, reintentando...")
                    await asyncio.sleep(0.5)
                    continue
                self.save_frame_for_display(frame)
                base64_frame = self.frame_to_base64(frame)
                if base64_frame is None:
                    await asyncio.sleep(0.5)
                    continue
                fatigue_data = await self.send_frame_to_server(base64_frame)
                await self.process_fatigue_detection(fatigue_data)
                await asyncio.sleep(0.5)
            except KeyboardInterrupt:
                print("Detención solicitada por el usuario")
                break
            except Exception as e:
                print(f"Error en bucle de detección: {e}")
                await asyncio.sleep(0.5)

    async def start(self):
        print("Iniciando sistema de detección de fatiga...")
        if not await self.connect_websocket():
            print("No se pudo conectar al servidor de detección")
            return
        await self.run_detection_loop()

    def stop(self):
        self.is_running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())

async def main():
    try:
        detector = CameraFatigueDetector()  # Detección automática de cámara
        await detector.start()
    except KeyboardInterrupt:
        print("Detención solicitada")
    except RuntimeError as e:
        print(f"Error: {e}")
        print("Sugerencias:")
        print("  - Verifica que la cámara esté conectada")
        print("  - Ejecuta 'ls /dev/video*' para ver dispositivos disponibles")
        print("  - Asegúrate de que la cámara no esté siendo usada por otra aplicación")
    finally:
        if 'detector' in locals():
            detector.stop()

if __name__ == "__main__":
    asyncio.run(main()) 
