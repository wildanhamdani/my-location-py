import requests
import subprocess
import re
import argparse

def get_lat_long(api_key, wifi_access_points=None, cell_towers=None):
    """
    Get the latitude and longitude using Google Maps Geolocation API.
    
    :param api_key: Your Google Maps Geolocation API key.
    :param wifi_access_points: A list of WiFi access point dictionaries with keys "macAddress", "signalStrength", and optionally "signalToNoiseRatio".
    :param cell_towers: A list of cell tower dictionaries with required keys "cellId", "locationAreaCode", "mobileCountryCode", and "mobileNetworkCode".
    :return: A dictionary with latitude and longitude.
    """
    
    url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' + api_key
    data = {}
    
    if wifi_access_points:
        data['wifiAccessPoints'] = wifi_access_points
    if cell_towers:
        data['cellTowers'] = cell_towers

    response = requests.post(url, json=data)
    location = response.json()
    
    if response.status_code == 200:
        return location['location']
    else:
        return location  # Return the error message if the request was not successful

def get_wifi_access_points(interface='wlan0'):
    """
    Get a list of WiFi access points with their MAC address and signal strength.

    :param interface: The network interface to use for scanning (default is 'wlan0').
    :return: A list of dictionaries, each containing 'macAddress' and 'signalStrength'.
    """
    # Run the iwlist command to scan for WiFi networks
    result = subprocess.run(['sudo', 'iwlist', interface, 'scan'], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception("Failed to run iwlist scan. Make sure you have sudo privileges.")

    # Regular expressions to match MAC addresses and signal strength
    mac_address_re = re.compile(r'Address: ([\da-fA-F:]{17})')
    signal_strength_re = re.compile(r'Signal level=(-?\d+) dBm')

    access_points = []
    current_ap = {}

    # Parse the output line by line
    for line in result.stdout.splitlines():
        mac_address_match = mac_address_re.search(line)
        if mac_address_match:
            if current_ap:
                access_points.append(current_ap)
                current_ap = {}
            current_ap['macAddress'] = mac_address_match.group(1)

        signal_strength_match = signal_strength_re.search(line)
        if signal_strength_match:
            current_ap['signalStrength'] = int(signal_strength_match.group(1))

    if current_ap:
        access_points.append(current_ap)

    return access_points

if __name__ == '__main__':
    # Example

    #api key as argument
    parser = argparse.ArgumentParser(description='Get location using Google Maps Geolocation API.')
    parser.add_argument('--api_key', type=str, help='Your Google Maps Geolocation API key.')
    parser.add_argument('--interface', type=str, default='wlan0', help='The network interface to use for scanning (default is wlan0).')
    args = parser.parse_args()

    wifi_access_points = get_wifi_access_points(args.interface)
    location = get_lat_long(args.api_key, wifi_access_points=wifi_access_points)
    print(location)
    print(f"{location['lat']}, {location['lng']}")

