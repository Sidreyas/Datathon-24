from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os

app = FastAPI()

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Load sample data
def load_data():
    with open(os.path.join("data", "sample_data.json"), "r") as f:
        return json.load(f)

@app.get("/")
async def read_dashboard(request: Request):
    data = load_data()
    return templates.TemplateResponse("index.html", {"request": request, "data": data})

@app.get("/api/overview")
async def get_overview():
    data = load_data()
    return data["overview"]

@app.get("/api/recent_detections")
async def get_recent_detections():
    data = load_data()
    return data["recent_detections"]

@app.get("/api/trend_data")
async def get_trend_data():
    data = load_data()
    return data["trend_data"]

@app.get("/api/deepfake_types")
async def get_deepfake_types():
    data = load_data()
    return data["deepfake_types"]
