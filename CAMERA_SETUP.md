# Configuración de Cámara - Sistema de Detección de Fatiga

## 🎯 Problema Resuelto

El sistema ahora detecta automáticamente la cámara disponible, eliminando la necesidad de configurar manualmente el dispositivo `/dev/video*` después de cada reinicio.

## 🔧 Cambios Implementados

### 1. Detección Automática de Cámara
- **Archivo modificado**: `camera_capture.py`
- **Función nueva**: `find_available_camera()`
- **Comportamiento**: Prueba automáticamente `/dev/video0`, `/dev/video1`, `/dev/video2`, `/dev/video3` y otros dispositivos disponibles

### 2. Script de Diagnóstico
- **Archivo nuevo**: `check_cameras.py`
- **Función**: Verifica el estado de todas las cámaras del sistema
- **Uso**: `python check_cameras.py`

### 3. Script de Inicio Mejorado
- **Archivo nuevo**: `start_servers_with_camera_check.sh`
- **Función**: Ejecuta diagnóstico antes de iniciar el sistema
- **Uso**: `./start_servers_with_camera_check.sh`

## 🚀 Cómo Usar

### Opción 1: Inicio Normal (Recomendado)
```bash
cd FatigueDetector
./start_servers.sh
```
El sistema detectará automáticamente la cámara disponible.

### Opción 2: Inicio con Diagnóstico
```bash
cd FatigueDetector
./start_servers_with_camera_check.sh
```
Ejecuta un diagnóstico completo antes de iniciar.

### Opción 3: Solo Diagnóstico
```bash
cd FatigueDetector
python check_cameras.py
```
Para verificar el estado de las cámaras sin iniciar el sistema.

## 🔍 Diagnóstico de Problemas

### Si la cámara no se detecta:

1. **Verificar conexión física**:
   ```bash
   ls /dev/video*
   ```

2. **Verificar permisos**:
   ```bash
   ls -la /dev/video*
   ```

3. **Instalar herramientas de diagnóstico**:
   ```bash
   sudo apt update
   sudo apt install v4l-utils
   ```

4. **Verificar información detallada**:
   ```bash
   v4l2-ctl --list-devices
   ```

5. **Dar permisos al usuario**:
   ```bash
   sudo usermod -a -G video $USER
   # Reiniciar sesión después
   ```

### Mensajes de Error Comunes

- `No se encontró ninguna cámara disponible`: La cámara no está conectada o no tiene permisos
- `/dev/videoX no puede leer frames`: La cámara está ocupada por otra aplicación
- `v4l2-ctl no está instalado`: Instalar con `sudo apt install v4l-utils`

## 📋 Logs del Sistema

El sistema ahora muestra mensajes informativos:

```
Detectando cámara disponible...
  Probando /dev/video0...
Cámara encontrada en /dev/video0
Usando cámara en /dev/video0
```

## 🔧 Configuración Avanzada

### Usar un dispositivo específico
Si necesitas usar un dispositivo específico, modifica la línea en `camera_capture.py`:

```python
detector = CameraFatigueDetector(camera_device=0)  # Usar /dev/video0
```

### Agregar más dispositivos a la búsqueda
Modifica la lista `common_devices` en la función `find_available_camera()`:

```python
common_devices = [0, 1, 2, 3, 4, 5]  # Agregar más dispositivos
```

## 🎯 Compatibilidad

- ✅ Cámaras USB (Logitech, etc.)
- ✅ Cámaras integradas de Raspberry Pi
- ✅ Múltiples cámaras conectadas
- ✅ Detección automática después de reinicio

## 📞 Soporte

Si tienes problemas:

1. Ejecuta `python check_cameras.py` para diagnóstico
2. Verifica que la cámara esté conectada y funcione
3. Asegúrate de que no esté siendo usada por otra aplicación
4. Verifica los permisos del usuario 
