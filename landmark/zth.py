import json
import requests
from bs4 import BeautifulSoup
import os

# 目标网页URL
WIKI_URL = "https://wiki.ria.red/wiki/%E6%A8%A1%E6%9D%BF:%E9%9B%B6%E6%B4%B2%E5%85%B1%E9%B8%A3%E5%9C%B0%E6%A0%87"
# 坐标数据源URL
COORDINATES_URL = "https://satellite.ria.red/map/_zth/tiles/_markers_/marker_world.json"

def parse_landmarks_to_json(wiki_url, coordinates_url):
    """
    Get and parse landmark data and coordinates from the given URLs, then return JSON format string.
    """
    try:
        # 1. 获取并解析坐标数据
        coords_response = requests.get(coordinates_url)
        coords_response.raise_for_status()
        coords_data = coords_response.json()

        coordinates_map = {}
        # 提取 "共鸣地标" (Tori) 中的标记点信息
        if 'sets' in coords_data and 'Tori' in coords_data['sets'] and 'markers' in coords_data['sets']['Tori']:
            for marker_id, marker_info in coords_data['sets']['Tori']['markers'].items():
                name = marker_info.get('label')
                if name:
                    coordinates_map[name] = {
                        "x": marker_info.get('x', 'Unknown'),
                        "y": marker_info.get('y', 'Unknown'),
                        "z": marker_info.get('z', 'Unknown')
                    }

        # 2. 获取并解析Wiki地标信息
        wiki_response = requests.get(wiki_url)
        wiki_response.raise_for_status()

        soup = BeautifulSoup(wiki_response.text, 'html.parser')
        landmark_items = soup.select('.navbox-inner .navbox-list li')

        landmarks_data = []
        landmark_id = 0

        for item in landmark_items:
            landmark_id += 1
            name_tag = item.find('a')
            
            if not name_tag:
                continue

            name = name_tag.get('title', name_tag.get_text(strip=True))

            grade = "Unknown"
            grade_tag = item.find('small')
            if grade_tag and grade_tag.get('aria-label'):
                grade = grade_tag['aria-label']

            status = "Normal"
            if item.find('span', style="text-decoration:line-through;"):
                status = "Removed"

            # 3. 匹配并添加坐标
            coordinates = coordinates_map.get(name, {"x": "Unknown", "y": "Unknown", "z": "Unknown"})

            landmarks_data.append({
                "id": landmark_id,
                "name": name,
                "grade": grade,
                "status": status,
                "coordinates": coordinates
            })

        return landmarks_data

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}
    except Exception as e:
        return {"error": f"An error occurred during processing: {e}"}

# 执行函数并保存结果
def save_landmarks_data():
    """
    Get landmark data and save it to JSON file.
    """
    landmarks_data = parse_landmarks_to_json(WIKI_URL, COORDINATES_URL)
    
    # 创建保存目录
    output_dir = "./data/landmark"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存到JSON文件
    output_file = os.path.join(output_dir, "zth.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(landmarks_data, f, ensure_ascii=False, indent=4)
    
    print(f"Landmark data saved to: {output_file}")
    print(f"Total landmarks: {len(landmarks_data) if isinstance(landmarks_data, list) else 'Error occurred'}")

if __name__ == "__main__":
    save_landmarks_data()