#!/usr/bin/env python3
import requests
import json
import time

def send_fatigue_level_1():
    """Send fatigue level 1 to Flask server"""
    fatigue_data = {
        "json_report": json.dumps({
            "timestamp": "2025-06-18 18:00:00",
            "yawn": {
                "report": True,
                "count": 1,
                "durations": [2.5]
            },
            "eye_rub_first_hand": {
                "report": False,
                "count": 0,
                "durations": []
            },
            "eye_rub_second_hand": {
                "report": False,
                "count": 0,
                "durations": []
            },
            "flicker": {
                "report": False,
                "count": 0
            },
            "micro_sleep": {
                "report": False,
                "count": 0,
                "durations": []
            },
            "pitch": {
                "report": False,
                "count": 0,
                "durations": []
            }
        })
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/fatigue/data',
            json=fatigue_data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS! Fatigue level: {result.get('fatigue_level', 'Unknown')}")
            return result.get('fatigue_level')
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"ERROR sending fatigue data: {e}")
        return None

def send_fatigue_level_0():
    """Send fatigue level 0 to Flask server"""
    fatigue_data = {
        "json_report": json.dumps({
            "timestamp": "2025-06-18 18:00:00",
            "yawn": {
                "report": False,
                "count": 0,
                "durations": []
            },
            "eye_rub_first_hand": {
                "report": False,
                "count": 0,
                "durations": []
            },
            "eye_rub_second_hand": {
                "report": False,
                "count": 0,
                "durations": []
            },
            "flicker": {
                "report": False,
                "count": 0
            },
            "micro_sleep": {
                "report": False,
                "count": 0,
                "durations": []
            },
            "pitch": {
                "report": False,
                "count": 0,
                "durations": []
            }
        })
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/fatigue/data',
            json=fatigue_data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS! Fatigue level: {result.get('fatigue_level', 'Unknown')}")
            return result.get('fatigue_level')
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"ERROR sending fatigue data: {e}")
        return None

if __name__ == "__main__":
    print("Testing 3 consecutive fatigue level 1 detections...")
    print("Make sure Flask server is running on localhost:5000")
    print("Open http://localhost:5000 in browser to see the button")
    print()
    
    # Send 3 consecutive fatigue level 1 detections
    for i in range(3):
        print(f"Sending detection {i+1}/3...")
        level = send_fatigue_level_1()
        if level != 1:
            print("FAILED! Detection not working properly")
            exit(1)
        time.sleep(2)  # Wait 2 seconds between detections
    
    print()
    print("SUCCESS! Sent 3 consecutive fatigue level 1 detections")
    print("Check the web interface - you should see:")
    print("   - Red background")
    print("   - 'Stop to Rest' button in center")
    print("   - Status: Cansado")
    print()
    print("Now testing counter reset with level 0...")
    time.sleep(2)
    
    # Send a level 0 to test counter reset
    print("Sending fatigue level 0...")
    send_fatigue_level_0()
    
    print()
    print("Now testing that counter resets - sending 2 level 1s then 1 level 0:")
    
    # Test counter reset
    for i in range(2):
        print(f"Sending level 1 detection {i+1}/2...")
        send_fatigue_level_1()
        time.sleep(1)
    
    print("Sending level 0 to reset counter...")
    send_fatigue_level_0()
    time.sleep(1)
    
    print("Now sending 3 consecutive level 1s again...")
    for i in range(3):
        print(f"Sending detection {i+1}/3...")
        send_fatigue_level_1()
        time.sleep(1)
    
    print()
    print("Test completed! The button should appear after the 3rd consecutive detection.") 
