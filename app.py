from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import json
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Query


app = FastAPI()

# Ensure 'reports' directory exists
if not os.path.exists("reports"):
    os.makedirs("reports")

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Load and filter data functions
def load_data():
    with open(os.path.join("data", "sample_data.json"), "r") as f:
        return json.load(f)

def filter_detections(data, year=None, month=None, media_type=None, status=None):
    detections = data["recent_detections"]
    filtered = []

    for detection in detections:
        detection_date = datetime.strptime(detection["timestamp"], "%Y-%m-%d %H:%M")
        if year and detection_date.year != year:
            continue
        if month and detection_date.month != month:
            continue
        if media_type and detection["media_type"] != media_type:
            continue
        if status and detection["status"] != status:
            continue
        filtered.append(detection)
    
    return filtered

# Report generation functions
def generate_csv_report(filtered_data, filename):
    df = pd.DataFrame(filtered_data)
    csv_path = os.path.join("reports", filename)
    df.to_csv(csv_path, index=False)
    return csv_path

def generate_pdf_report(filtered_data, filename):
    pdf_path = os.path.join("reports", filename)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    text = c.beginText(50, height - 50)
    text.textLine("Deepfake Detection Report")
    text.textLine(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    text.textLine("")

    for detection in filtered_data:
        line = f"ID: {detection['id']}, Type: {detection['media_type']}, Timestamp: {detection['timestamp']}, Status: {detection['status']}, Confidence: {detection['confidence_score']*100:.2f}%, Details: {detection['details']}"
        text.textLine(line)
        if text.getY() < 50:
            c.drawText(text)
            c.showPage()
            text = c.beginText(50, height - 50)
    
    c.drawText(text)
    c.save()
    return pdf_path

    
    
# API Endpoints
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


@app.get("/api/recent_detections_filtered")
async def get_recent_detections_filtered(
    year: int = Query(None, ge=2000, le=2100, description="Filter by year (e.g., 2024)"),
    month: int = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    media_type: str = Query(
        None, 
        regex="^(Video|Audio|Image|Other)$", 
        description="Filter by media type (Video, Audio, Image, Other)"
    ),
    status: str = Query(
        None, 
        regex="^(Real|Fake)$", 
        description="Filter by status (Real or Fake)"
    )
):
    data = load_data()
    filtered = filter_detections(data, year, month, media_type, status)
    return filtered


@app.get("/api/trend_data")
async def get_trend_data():
    data = load_data()
    return data["trend_data"]

@app.get("/api/trend_data_filtered")
async def get_trend_data_filtered(year: int = None, month: int = None):
    data = load_data()
    detections = data["recent_detections"]
    trend = {}

    for detection in detections:
        detection_date = datetime.strptime(detection["timestamp"], "%Y-%m-%d %H:%M")
        if year and detection_date.year != year:
            continue
        if month and detection_date.month != month:
            continue
        date_str = detection_date.strftime("%Y-%m-%d")
        trend[date_str] = trend.get(date_str, 0) + 1

    # Sort dates
    sorted_dates = sorted(trend.keys())
    sorted_counts = [trend[date] for date in sorted_dates]

    return {"dates": sorted_dates, "detections": sorted_counts}

@app.get("/api/deepfake_types")
async def get_deepfake_types():
    data = load_data()
    return data["deepfake_types"]

    
@app.get("/api/generate_report")
async def generate_report(format: str = "csv", year: int = None, month: int = None, media_type: str = None, status: str = None):
    data = load_data()
    filtered = filter_detections(data, year, month, media_type, status)
    
    if format == "csv":
        filename = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        path = generate_csv_report(filtered, filename)
        return FileResponse(path, media_type='text/csv', filename=filename)
    elif format == "pdf":
        filename = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        path = generate_pdf_report(filtered, filename)
        return FileResponse(path, media_type='application/pdf', filename=filename)
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Choose 'csv' or 'pdf'.")


    