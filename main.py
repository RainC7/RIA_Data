import json
import uvicorn
import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
from wiki.search_parser import parse_wiki_search_results

app = FastAPI()

# Mount the static directory to serve frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load landmark data
def load_data(source: str):
    try:
        if source == "zth":
            with open("data/landmark/zth.json", "r", encoding="utf-8") as f:
                return json.load(f)
        elif source == "houtu":
            with open("data/landmark/houtu.json", "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return []
    except FileNotFoundError:
        return []

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.get("/api/landmarks")
async def get_landmarks(source: str = Query("zth", description="Data source (zth or houtu)"), name: Optional[str] = Query(None, description="Filter by landmark name containing the given string (case-insensitive)")):
    landmarks = load_data(source)
    if name:
        landmarks = [lm for lm in landmarks if name.lower() in lm['name'].lower()]
    return landmarks

@app.get("/api/landmarks/{landmark_id}")
async def get_landmark_by_id(landmark_id: int, source: str = Query("zth", description="Data source (zth or houtu)")):
    landmarks = load_data(source)
    for landmark in landmarks:
        if landmark["id"] == landmark_id:
            return landmark
    return {"error": "Landmark not found"}

@app.get("/api/wiki_search")
async def search_wiki(query: str = Query(..., description="Search query for RIA Wiki")):
    WIKI_SEARCH_URL = f"https://wiki.ria.red/index.php?search={query}&title=%E7%89%B9%E6%AE%8A:%E6%90%9C%E7%B4%A2&go=%E5%89%8D%E5%BE%80"
    try:
        response = requests.get(WIKI_SEARCH_URL)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        search_results = parse_wiki_search_results(response.text)
        return search_results
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wiki search results: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing wiki search results: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)