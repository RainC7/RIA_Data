import json
from enum import Enum
from pathlib import Path
from typing import Optional

import requests
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from wiki.search_parser import parse_wiki_search_results

class Server(str, Enum):
    zth = "zth"
    naraku = "naraku"
    houtu = "houtu"


DATA_DIRECTORIES = {
    "landmark": Path("data/landmark"),
    "railway": Path("data/railway"),
}


app = FastAPI(title="RIA_Data")

# Mount the static directory to serve frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")


def load_dataset(dataset: str, server: Server):
    """
    Load the requested dataset for a given server.
    """
    directory = DATA_DIRECTORIES.get(dataset)
    if not directory:
        return []

    file_path = directory / f"{server.value}.json"
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def resolve_server(
    server: Optional[str] = Query(
        None,
        description="莉亚服务器：zth、naraku、houtu",
    ),
    legacy_source: Optional[str] = Query(
        None,
        alias="source",
        include_in_schema=False,
        description="已废弃参数 source，仍可兼容旧请求",
    ),
) -> Server:
    """
    Resolve the server parameter, keeping backward compatibility with the old `source`.
    """
    selected = server or legacy_source or Server.zth.value
    try:
        return Server(selected)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid server '{selected}'. Allowed values: zth, naraku, houtu",
        )


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/api/landmarks")
async def get_landmarks(
    server: Server = Depends(resolve_server),
    name: Optional[str] = Query(
        None,
        description="Filter by landmark name containing the given string (case-insensitive)",
    ),
):
    landmarks = load_dataset("landmark", server)
    if name:
        landmarks = [lm for lm in landmarks if name.lower() in lm["name"].lower()]
    return landmarks

@app.get("/api/landmarks/{landmark_id}")
async def get_landmark_by_id(
    landmark_id: str,
    server: Server = Depends(resolve_server),
):
    landmarks = load_dataset("landmark", server)
    for landmark in landmarks:
        if str(landmark.get("id")) == landmark_id:
            return landmark
    raise HTTPException(status_code=404, detail="Landmark not found")

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


@app.get("/api/railways")
async def get_railways(
    server: Server = Depends(resolve_server),
    name: Optional[str] = Query(
        None,
        description="Filter by station name or line identifier (case-insensitive)",
    ),
):
    stations = load_dataset("railway", server)
    if name:
        keyword = name.lower()
        filtered = []
        for station in stations:
            station_name = station.get("stationName", "")
            lines = station.get("lines", [])
            if keyword in station_name.lower() or any(
                keyword
                in (
                    f"{line.get('bureau', '')}{line.get('line', '')}{line.get('stationCode', '')}".lower()
                )
                for line in lines
            ):
                filtered.append(station)
        stations = filtered
    return stations


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
