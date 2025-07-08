import requests
import json
from bs4 import BeautifulSoup
import os

def get_wiki_landmarks(url):
    """
    Parses the RIA Wiki page to extract landmark names and their corresponding regions.

    Args:
        url (str): The URL of the wiki page.

    Returns:
        dict: A dictionary with region names as keys and lists of landmark names as values.
              Returns an empty dictionary if there's an error.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the wiki page at {url}: {e}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    
    landmarks_by_region = {}
    
    # Find the navigation box containing the landmark data
    navbox = soup.find('table', class_='navbox-houtu_landmarks')
    if not navbox:
        print("Could not find the landmark table on the wiki page.")
        return {}
        
    # Iterate over the rows in the table body
    for row in navbox.find_all('tr'):
        region_th = row.find('th', class_='navbox-group')
        landmarks_td = row.find('td', class_='navbox-list-with-group')
        
        if region_th and landmarks_td:
            region_name = region_th.get_text(strip=True)
            landmark_links = landmarks_td.find_all('a')
            # Extract names from the text of the <a> tags
            landmark_names = [link.get_text(strip=True) for link in landmark_links]
            
            if region_name:
                landmarks_by_region[region_name] = landmark_names
                
    return landmarks_by_region

def get_landmark_coordinates(url):
    """
    Fetches and parses landmark coordinates from the provided JSON data source.

    Args:
        url (str): The URL of the coordinates JSON file.

    Returns:
        dict: A dictionary mapping landmark labels to their coordinates.
              Returns an empty dictionary if there's an error.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching or parsing coordinates JSON from {url}: {e}")
        return {}
        
    coordinates = {}
    # Navigate through the JSON structure to find the markers
    markers = data.get('sets', {}).get('Tori', {}).get('markers', {})
    
    for marker_data in markers.values():
        label = marker_data.get('label')
        if label:
            # Store coordinates by landmark label for easy lookup
            coordinates[label] = {
                'x': marker_data.get('x', 'Unknown'),
                'y': marker_data.get('y', 'Unknown'),
                'z': marker_data.get('z', 'Unknown')
            }
            
    return coordinates

def format_landmarks_data(wiki_data, coords_data):
    """
    Combines and formats the landmark data from the wiki and coordinates source
    into the final specified JSON structure.

    Args:
        wiki_data (dict): Data parsed from the wiki.
        coords_data (dict): Data parsed from the coordinates JSON.

    Returns:
        list: A list of dictionaries, each representing a formatted landmark.
    """
    region_prefixes = {
        "中大陆": "C",
        "北大陆": "N",
        "东大陆": "E",
        "东南陆缘": "ES",
        "西南陆缘": "WS",
        "西大陆": "W",
    }
    
    # A mapping to handle inconsistencies between wiki names and JSON labels
    name_mapping = {
        "后土交通局一号展示场": "交通局1号展场"
    }

    # Initialize counters for generating unique IDs for each region
    counters = {prefix: 1 for prefix in region_prefixes.values()}
    formatted_data = []

    # Iterate through each region and its landmarks from the wiki data
    for region, landmarks in wiki_data.items():
        prefix = region_prefixes.get(region)
        if not prefix:
            continue
            
        for landmark_name in landmarks:
            # Generate the unique ID based on region and counter
            landmark_id = f"{prefix}-{counters[prefix]:02d}"
            counters[prefix] += 1
            
            # Find coordinates, using the name mapping if necessary
            lookup_name = name_mapping.get(landmark_name, landmark_name)
            coords = coords_data.get(lookup_name, {"x": "Unknown", "y": "Unknown", "z": "Unknown"})

            # Append the fully formatted landmark object to our list
            formatted_data.append({
                "id": landmark_id,
                "name": landmark_name,
                "grade": "白级",
                "status": "Normal",
                "coordinates": coords
            })
            
    return formatted_data

def save_landmarks_data():
    """
    Get landmark data and save it to JSON file.
    """
    WIKI_URL = "https://wiki.ria.red/wiki/%E6%A8%A1%E6%9D%BF:%E5%90%8E%E5%9C%9F%E6%B4%B2%E5%85%B1%E9%B8%A3%E5%9C%B0%E6%A0%87"
    COORDINATES_URL = "https://satellite.ria.red/map/_houtu/tiles/_markers_/marker_world.json"

    # Step 1: Get landmark data from the wiki
    wiki_landmarks = get_wiki_landmarks(WIKI_URL)
    
    # Step 2: Get coordinate data from the JSON source
    landmark_coords = get_landmark_coordinates(COORDINATES_URL)
    
    # Step 3: Combine, format, and prepare the final data
    if wiki_landmarks and landmark_coords:
        final_data = format_landmarks_data(wiki_landmarks, landmark_coords)
        
        # Step 4: Create output directory and save to JSON file
        output_dir = "./data/landmark"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, "houtu.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"Landmark data saved to: {output_file}")
        print(f"Total landmarks: {len(final_data)}")
    else:
        print("Failed to get landmark data")

if __name__ == '__main__':
    save_landmarks_data()