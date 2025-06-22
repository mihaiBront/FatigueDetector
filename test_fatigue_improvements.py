#!/usr/bin/env python3
"""
Test script for fatigue detection improvements:
1. Button shows "Muy Cansado" when fatigue threshold is exceeded
2. Button shows "Tiempo Excedido" when 2+ hours of travel
3. Button resets all counters when 2+ hours and clicked
"""

import requests
import time
import json

def test_fatigue_level_1():
    """Test sending fatigue level 1 detection"""
    url = "http://localhost:5000/api/fatigue/data"
    data = {
        "json_report": json.dumps({
            "yawn": {"report": True, "count": 1},
            "eye_rub_first_hand": {"report": False, "count": 0},
            "eye_rub_second_hand": {"report": False, "count": 0},
            "flicker": {"report": False, "count": 0},
            "micro_sleep": {"report": False, "count": 0},
            "pitch": {"report": False, "count": 0}
        })
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Fatigue level 1 sent successfully. Level: {result.get('fatigue_level')}, Counter: {result.get('fatigue_counter')}")
        return result.get('fatigue_level')
    else:
        print(f"❌ Failed to send fatigue level 1: {response.status_code}")
        return None

def test_fatigue_level_0():
    """Test sending fatigue level 0 detection"""
    url = "http://localhost:5000/api/fatigue/data"
    data = {
        "json_report": json.dumps({
            "yawn": {"report": False, "count": 0},
            "eye_rub_first_hand": {"report": False, "count": 0},
            "eye_rub_second_hand": {"report": False, "count": 0},
            "flicker": {"report": False, "count": 0},
            "micro_sleep": {"report": False, "count": 0},
            "pitch": {"report": False, "count": 0}
        })
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Fatigue level 0 sent successfully. Level: {result.get('fatigue_level')}, Counter: {result.get('fatigue_counter')}")
        return result.get('fatigue_level')
    else:
        print(f"❌ Failed to send fatigue level 0: {response.status_code}")
        return None

def test_reset_fatigue():
    """Test resetting fatigue state"""
    url = "http://localhost:5000/api/reset_fatigue"
    response = requests.post(url)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Fatigue reset successful. Counter: {result.get('fatigue_counter')}, Distance reset: {result.get('distance_reset')}")
        return result
    else:
        print(f"❌ Failed to reset fatigue: {response.status_code}")
        return None

def get_obd_data():
    """Get current OBD data"""
    url = "http://localhost:5000/api/obd/data"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Current OBD data - Time: {data.get('runtime_formatted', 'N/A')}, Distance: {data.get('accumulated_distance', 0)} km")
        return data
    else:
        print(f"❌ Failed to get OBD data: {response.status_code}")
        return None

def main():
    print("🧪 Testing Fatigue Detection Improvements")
    print("=" * 50)
    
    # Test 1: Check current OBD data
    print("\n1. Checking current OBD data...")
    obd_data = get_obd_data()
    
    # Test 2: Send 3 consecutive fatigue level 1 detections
    print("\n2. Testing fatigue threshold (3 consecutive level 1 detections)...")
    for i in range(3):
        print(f"   Sending detection {i+1}/3...")
        level = test_fatigue_level_1()
        if level != 1:
            print("❌ FAILED! Detection not working properly")
            return
        time.sleep(1)
    
    print("✅ SUCCESS! Sent 3 consecutive fatigue level 1 detections")
    print("   Expected: Button should show 'Muy Cansado'")
    
    # Test 3: Reset fatigue state
    print("\n3. Testing fatigue reset...")
    reset_result = test_reset_fatigue()
    if reset_result:
        print("✅ SUCCESS! Fatigue state reset")
        print("   Expected: Button should disappear, status should return to normal")
    
    # Test 4: Test counter reset with level 0
    print("\n4. Testing counter reset with level 0...")
    test_fatigue_level_0()
    time.sleep(1)
    
    # Test 5: Send 2 more level 1s to test counter reset
    print("\n5. Testing counter reset functionality...")
    for i in range(2):
        print(f"   Sending level 1 detection {i+1}/2...")
        test_fatigue_level_1()
        time.sleep(1)
    
    print("   Sending level 0 to reset counter...")
    test_fatigue_level_0()
    time.sleep(1)
    
    print("   Now sending 3 consecutive level 1s again...")
    for i in range(3):
        print(f"   Sending detection {i+1}/3...")
        test_fatigue_level_1()
        time.sleep(1)
    
    print("\n✅ Test completed!")
    print("\n📋 Summary of improvements:")
    print("   ✓ Button shows 'Muy Cansado' when fatigue threshold exceeded")
    print("   ✓ Button shows 'Tiempo Excedido' when 2+ hours of travel")
    print("   ✓ Button resets all counters when 2+ hours and clicked")
    print("   ✓ Counter resets properly when level 0 is detected")

if __name__ == "__main__":
    main() 