from flet import *
import asyncio
import websockets
import json
import cv2
import numpy as np
import threading
import base64
import tkinter as tk
from PIL import Image as PILImage, ImageTk
import os  # Para el pitido en Mac/Linux
import time

from gui.resources.resources_path import (ImagePaths, FontsPath)


class Drowsiness:
    def __init__(self, page):
        self.page = page

        self.running = True  # Always running
        self.video_thread = None
        self.original_image_control = None
        self.mouth_status_text = None

        self.images = ImagePaths()
        self.fonts = FontsPath()

        self.uri = "ws://localhost:8000/ws"
        self.cap = None
        self.alert_running = False
        self.yawn_detected = False
        self.last_yawn_time = 0  # Track last yawn time
        self.alert_thread = None  # Thread for continuous alert
        self.mouth_open = False  # Track mouth state
        self.mouth_open_time = 0

    def main(self):
        # Configuración de la ventana sin mensajes de créditos
        self.page.title = "Driver Fatigue Detection"
        self.page.window_width = 800  # Reduced width since we only have one view
        self.page.window_height = 720
        self.page.window_resizable = False
        self.page.update()

        self.original_image_control = Image(
            width=640,
            height=480,
            fit=ImageFit.COVER,
            src_base64=self.get_placeholder_image()
        )

        self.mouth_status_text = Text(
            "Estado de la boca: Cerrada",
            size=30,
            color="white",
            weight="bold"
        )

        main_column = Column(
            controls=[
                Container(height=30),
                self.original_image_control,
                Container(height=20),
                self.mouth_status_text,
            ],
            alignment='center',
            horizontal_alignment='center',
            spacing=20,
            expand=True
        )

        elements = Container(
            content=Row(
                controls=[
                    main_column
                ],
                alignment='center',
                vertical_alignment='center',
            ),
            bgcolor="#807da6",
            padding=0,
            expand=True
        )

        # Start detection automatically
        self.video_thread = threading.Thread(target=self.run_detection, daemon=True)
        self.video_thread.start()

        return elements

    def run_detection(self):
        self.cap = cv2.VideoCapture(0)
        asyncio.run(self.process_video(self.uri, self.cap))
        if self.cap is not None:
            self.cap.release()

    def get_placeholder_image(self):
        drowsiness_image = cv2.imread(self.images.image_5)
        _, buffer = cv2.imencode('.jpg', drowsiness_image)
        blank_base64 = base64.b64encode(buffer).decode('utf-8')
        return blank_base64

    def cv2_to_base64(self, image):
        _, img_buffer = cv2.imencode(".jpg", image)
        return base64.b64encode(img_buffer).decode('utf-8')

    def play_continuous_alert(self):
        """Reproduce un pitido continuo durante 5 segundos"""
        start_time = time.time()
        while time.time() - start_time < 5:
            try:
                os.system('afplay /System/Library/Sounds/Ping.aiff')
                time.sleep(0.5)  # Reproducir cada medio segundo
            except:
                try:
                    print('\a')
                    time.sleep(0.5)
                except:
                    pass

    async def process_video(self, uri, cap):
        async with websockets.connect(uri) as websocket:
            while self.running:  # Keep running until window is closed
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize frame to reduce size
                frame = cv2.resize(frame, (640, 480))
                
                # Compress the frame with lower quality
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')

                try:
                    # send frame
                    await websocket.send(frame_base64)

                    # receive response
                    response = await websocket.recv()
                    response_data = json.loads(response)

                    # Parsear el json_report que contiene los datos de detección
                    json_report_str = response_data.get("json_report", "{}")
                    try:
                        json_report = json.loads(json_report_str) if isinstance(json_report_str, str) else json_report_str
                        
                        # Buscar datos de bostezo en el json_report
                        if 'yawn' in json_report:
                            yawn_data = json_report['yawn']
                            
                            # Detectar bostezo basado en el conteo o reporte
                            yawn_count = yawn_data.get('count', 0)
                            yawn_report = yawn_data.get('report', False)
                            
                            # Debug: Imprimir datos de bostezo
                            print(f"Datos de bostezo - Count: {yawn_count}, Report: {yawn_report}")
                            
                            # Actualizar estado de la boca
                            previous_mouth_state = self.mouth_open
                            self.mouth_open = yawn_count > 0 or yawn_report
                            
                            # Debug: Imprimir cambio de estado
                            if previous_mouth_state != self.mouth_open:
                                print(f"Cambio de estado de boca: {previous_mouth_state} -> {self.mouth_open}")
                            
                            # Solo actualizar el texto si el estado ha cambiado
                            if previous_mouth_state != self.mouth_open:
                                self.mouth_status_text.value = f"Estado de la boca: {'Abierta' if self.mouth_open else 'Cerrada'}"
                                self.mouth_status_text.color = "red" if self.mouth_open else "white"
                                self.page.update()
                            
                            current_time = time.time()
                            # Si hay conteo de bostezos mayor a 0 o hay un reporte activo, y han pasado 5 segundos desde el último bostezo
                            if self.mouth_open and (current_time - self.last_yawn_time) >= 5:
                                self.yawn_detected = True
                                self.last_yawn_time = current_time
                                
                                # Activar alerta
                                self.page.bgcolor = "red"
                                self.page.update()
                                
                                # Iniciar pitido continuo en un hilo separado
                                if self.alert_thread is None or not self.alert_thread.is_alive():
                                    self.alert_thread = threading.Thread(target=self.play_continuous_alert)
                                    self.alert_thread.start()
                                
                                # Programar la restauración después de 5 segundos
                                def restore_normal():
                                    self.page.bgcolor = "#807da6"
                                    self.page.update()
                                
                                threading.Timer(5.0, restore_normal).start()
                                
                    except json.JSONDecodeError as e:
                        print(f"Error parseando json_report: {e}")

                    # image original
                    original_base64 = response_data.get("original_image")
                    original_data = base64.b64decode(original_base64)
                    nparr_original = np.frombuffer(original_data, np.uint8)
                    original_image = cv2.imdecode(nparr_original, cv2.IMREAD_COLOR)

                    # update image in Flet
                    self.original_image_control.src_base64 = self.cv2_to_base64(original_image)

                    # update UI
                    self.page.update()

                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"Error de conexión: {e}")
                    break
                except Exception as e:
                    print(f"Error inesperado: {e}")
                    break

                await asyncio.sleep(0.1)

    def restore_background(self):
        print("Restaurando fondo original")
        self.page.bgcolor = "#807da6"
        self.page.update()

    def setup_mouth_state_reset(self):
        """Setup timer for automatic mouth state reset"""
        self.mouth_reset_timer = threading.Timer(5.0, self.reset_mouth_state)
        self.mouth_reset_timer.daemon = True
        self.mouth_reset_timer.start()

    def reset_mouth_state(self):
        """Reset mouth state to closed"""
        self.mouth_status_text.value = "Estado de la boca: Cerrada"
        self.mouth_status_text.color = "white"
        self.page.update()
        self.mouth_open = False
        self.mouth_reset_timer.cancel()

    def update_mouth_state(self, is_open: bool):
        """Update mouth state with automatic reset"""
        current_time = time.time()
        
        if is_open:
            if not self.mouth_open:
                print(f"Boca abierta detectada en: {current_time}")
                self.mouth_open = True
                self.mouth_open_time = current_time
                self.mouth_status_text.value = "Estado de la boca: Abierta"
                self.mouth_status_text.color = "red"
                self.page.update()
        else:
            if self.mouth_open:
                print("Boca cerrada detectada")
                self.mouth_open = False
                self.mouth_status_text.value = "Estado de la boca: Cerrada"
                self.mouth_status_text.color = "green"
                self.page.update()
            
        # Reset after 5 seconds
        if self.mouth_open:
            elapsed_time = current_time - self.mouth_open_time
            print(f"Tiempo transcurrido: {elapsed_time:.2f} segundos")
            if elapsed_time >= 5.0:
                print("¡Reseteando estado de la boca después de 5 segundos!")
                self.mouth_open = False
                self.mouth_status_text.value = "Estado de la boca: Cerrada"
                self.mouth_status_text.color = "green"
                self.page.update()

    def process_frame(self, frame):
        """Process video frame and update UI"""
        if frame is None:
            return

        # Convert frame to RGB for processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Send frame to server
        success, response = self.send_frame(rgb_frame)
        
        if success:
            # Update drowsiness status
            self.update_drowsiness_status(response.get('drowsiness', False))
            
            # Update yawn count and reset if no yawn
            yawn_count = response.get('yawn_count', 0)
            mouth_open = response.get('mouth_open', False)
            
            if not mouth_open:
                # Reset everything when mouth is closed
                self.reset_all()
            else:
                print(f"Actualizando contador de bostezos a: {yawn_count}")
                self.yawn_count_text.value = f"Bostezos: {yawn_count}"
                self.page.update()
            
            # Update mouth state
            self.update_mouth_state(mouth_open)
            
            # Update video display
            self.update_video_display(frame)

    def setup_alert_sound(self):
        """Setup alert sound"""
        self.alert_sound = AudioPlayer()
        self.alert_sound.load("assets/alert.mp3")
        self.alert_sound.set_volume(1.0)  # Volumen máximo
        self.alert_sound.set_loop(True)  # Reproducir en bucle
        self.alert_timer = None

    def play_alert(self):
        """Play alert sound for 3 seconds"""
        if not self.alert_sound.is_playing():
            print("Iniciando alerta sonora")
            self.alert_sound.play()
            
            # Detener después de 3 segundos
            if self.alert_timer:
                self.alert_timer.cancel()
            self.alert_timer = threading.Timer(3.0, self.stop_alert)
            self.alert_timer.start()

    def stop_alert(self):
        """Stop alert sound"""
        print("Deteniendo alerta sonora")
        if hasattr(self, 'alert_sound'):
            self.alert_sound.stop()
        if hasattr(self, 'alert_timer') and self.alert_timer:
            self.alert_timer.cancel()
            self.alert_timer = None

    def update_drowsiness_status(self, is_drowsy: bool):
        """Update drowsiness status and trigger alert"""
        if is_drowsy:
            self.drowsiness_status_text.value = "Estado: Somnoliento"
            self.drowsiness_status_text.color = "red"
            self.play_alert()
        else:
            self.drowsiness_status_text.value = "Estado: Despierto"
            self.drowsiness_status_text.color = "green"
            self.stop_alert()
        self.page.update()

    def reset_all(self):
        """Reset all states and counters"""
        print("Reseteando todo el sistema")
        # Reset mouth state
        self.mouth_open = False
        self.mouth_status_text.value = "Estado de la boca: Cerrada"
        self.mouth_status_text.color = "green"
        
        # Reset yawn count
        self.yawn_count_text.value = "Bostezos: 0"
        
        # Stop alert sound
        self.stop_alert()
        
        # Update UI
        self.page.update()
