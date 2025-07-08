import json
import uvicorn
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional

app = FastAPI()

# Mount the static directory to serve frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load landmark data from JSON file
def load_data():
    try:
        with open("data/zth.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.get("/api/landmarks")
async def get_landmarks(name: Optional[str] = Query(None, description="Filter by landmark name containing the given string (case-insensitive)")):
    landmarks = load_data()
    if name:
        landmarks = [lm for lm in landmarks if name.lower() in lm['name'].lower()]
    return landmarks

@app.get("/api/landmarks/{landmark_id}")
async def get_landmark_by_id(landmark_id: int):
    landmarks = load_data()
    for landmark in landmarks:
        if landmark["id"] == landmark_id:
            return landmark
    return {"error": "Landmark not found"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)