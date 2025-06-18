import cv2
import base64
import numpy as np
import sys
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Add the driver_fatigue_detection-master directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'driver_fatigue_detection-master'))

from drowsiness_processor.main import DrowsinessDetectionSystem

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instance of the drowsiness detection system
drowsiness_system = None

@app.on_event("startup")
async def startup_event():
    global drowsiness_system
    drowsiness_system = DrowsinessDetectionSystem()
    print("Drowsiness detection system initialized")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # read data
            data = await websocket.receive_text()

            # decode data
            original_image, sketch, json_report = drowsiness_system.run(data)

            # Compress images before sending
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            _, buffer_sketch = cv2.imencode('.jpg', sketch, encode_param)
            sketch_base64 = base64.b64encode(buffer_sketch).decode('utf-8')

            _, buffer_original_image = cv2.imencode('.jpg', original_image, encode_param)
            original_image_base64 = base64.b64encode(buffer_original_image).decode('utf-8')

            # send answer
            await websocket.send_json({
                "json_report": json_report,
                "sketch_image": sketch_base64,
                "original_image": original_image_base64,
            })

    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fatigue_detection"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 