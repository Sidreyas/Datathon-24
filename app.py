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
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os
import matplotlib.pyplot as plt
import pandas as pd



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


def filter_detections(data, year=None, month=None, media_type=None, status=None, medium=None):
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
        if medium and detection["medium"] != medium:
            continue
        filtered.append(detection)
    
    return filtered


# Report generation functions
def generate_csv_report(filtered_data, filename):
    df = pd.DataFrame(filtered_data)
    csv_path = os.path.join("reports", filename)
    df.to_csv(csv_path, index=False)
    return csv_path

def generate_csv_report(filtered_data, filename):
    df = pd.DataFrame(filtered_data)
    csv_path = os.path.join("reports", filename)
    df.to_csv(csv_path, index=False)
    return csv_path

def add_trend_chart_to_pdf(data, elements):
    # Generate the chart
    plt.figure(figsize=(6, 3))
    plt.plot(data['dates'], data['detections'], marker='o', linestyle='-', color='blue')
    plt.title('Deepfake Detection Trends Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Detections')
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_path = 'reports/trend_chart.png'
    plt.savefig(chart_path)
    plt.close()
    
    # Add the chart to the PDF
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Detection Trends Over Time", styles['LeftHeading']))
    elements.append(Image(chart_path, width=6*inch, height=3*inch))
    elements.append(Spacer(1, 24))
import matplotlib.pyplot as plt
from reportlab.platypus import Image

def generate_pdf_report(filtered_data, filename):
    """
    Generates a structured PDF report resembling the dashboard layout.

    Parameters:
    - filtered_data (list of dict): The list of deepfake detections after applying filters.
    - filename (str): The name of the PDF file to be generated.
    
    Returns:
    - str: The file path to the generated PDF.
    """

    pdf_path = os.path.join("reports", filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=LETTER,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
    )
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', alignment=TA_CENTER, fontSize=18, spaceAfter=20))
    styles.add(ParagraphStyle(name='LeftHeading', alignment=TA_LEFT, fontSize=14, spaceAfter=10, textColor=colors.HexColor("#4F81BD")))
    styles.add(ParagraphStyle(name='TableHeader', alignment=TA_LEFT, fontSize=12, spaceAfter=5, fontName='Helvetica-Bold'))
    
    # Title
    title = Paragraph("Deepfake Detection Report", styles['CenterTitle'])
    elements.append(title)
    
    # Report Generation Time
    gen_time = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])
    elements.append(gen_time)
    elements.append(Spacer(1, 12))
    
    # Overview Metrics
    data = load_data()
    overview = data["overview"]  # Ensure load_data() is accessible here
    overview_data = [
        ["Total Media Processed", overview["total_media_processed"]],
        ["Total Deepfakes Detected", overview["total_deepfakes_detected"]],
        ["Detection Accuracy", f"{overview['detection_accuracy']}%"],
        ["False Positives", overview["false_positives"]],
        ["False Negatives", overview["false_negatives"]],
    ]
    
    elements.append(Paragraph("Overview Metrics", styles['LeftHeading']))
    
    overview_table = Table(overview_data, colWidths=[2.5 * inch, 2.5 * inch])
    overview_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(overview_table)
    elements.append(Spacer(1, 24))
    
    # Deepfake Detections by Medium
    elements.append(Paragraph("Deepfake Detections by Medium", styles['LeftHeading']))
    
    # Summarize detections by medium
    medium_counts = {}
    for detection in filtered_data:
        medium = detection.get("medium", "Other")
        medium_counts[medium] = medium_counts.get(medium, 0) + 1
    
    medium_data = [["Medium", "Number of Deepfakes Detected"]]
    for medium, count in medium_counts.items():
        medium_data.append([medium, count])
    
    medium_table = Table(medium_data, colWidths=[3 * inch, 2 * inch])
    medium_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2DCDB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(medium_table)
    elements.append(Spacer(1, 24))
    
    # Add Trend Chart
    elements.append(Paragraph("Detection Trends Over Time", styles['LeftHeading']))
    
    # Generate Trend Chart
    dates = [d['timestamp'] for d in filtered_data]
    dates = [datetime.strptime(d, "%Y-%m-%d %H:%M") for d in dates]
    date_counts = {}
    for date in dates:
        date_str = date.strftime("%Y-%m-%d")
        date_counts[date_str] = date_counts.get(date_str, 0) + 1
    sorted_dates = sorted(date_counts.keys())
    sorted_counts = [date_counts[date] for date in sorted_dates]
    
    plt.figure(figsize=(6, 3))
    plt.plot(sorted_dates, sorted_counts, marker='o', linestyle='-', color='blue')
    plt.title('Deepfake Detection Trends Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Detections')
    plt.xticks(rotation=45)
    plt.tight_layout()
    trend_chart_path = 'reports/trend_chart.png'
    plt.savefig(trend_chart_path)
    plt.close()
    
    # Add the trend chart image
    elements.append(Image(trend_chart_path, width=6*inch, height=3*inch))
    elements.append(Spacer(1, 24))
    
    # Detailed Detections Table
    elements.append(Paragraph("Detailed Deepfake Detections", styles['LeftHeading']))
    
    # Prepare data for the detailed table
    detailed_data = [
        [
            "ID",
            "Media Type",
            "Medium",
            "Timestamp",
            "Status",
            "Confidence Score",
            "Details",
        ]
    ]
    
    for detection in filtered_data:
        detailed_data.append([
            detection.get("id", ""),
            detection.get("media_type", ""),
            detection.get("medium", ""),
            detection.get("timestamp", ""),
            detection.get("status", ""),
            f"{detection.get('confidence_score', 0) * 100:.2f}%",
            detection.get("details", ""),
        ])
    
    # Convert to DataFrame for better handling (optional)
    df = pd.DataFrame(filtered_data)
    
    # Limit the number of rows per page to prevent overflow
    MAX_ROWS_PER_PAGE = 25
    total_rows = len(detailed_data)
    current_index = 0
    
    while current_index < total_rows:
        chunk = detailed_data[current_index: current_index + MAX_ROWS_PER_PAGE]
        table = Table(chunk, colWidths=[0.5 * inch, 1 * inch, 1 * inch, 1.5 * inch, 0.8 * inch, 1.2 * inch, 2.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#B6DDE8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 12))
        current_index += MAX_ROWS_PER_PAGE
        if current_index < total_rows:
            elements.append(PageBreak())
    
    # Remove the trend chart image file after embedding
    if os.path.exists(trend_chart_path):
        os.remove(trend_chart_path)
    
    # Build the PDF
    doc.build(elements)
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

@app.get("/api/deepfake_types_filtered")
async def get_deepfake_types_filtered(
    year: int = Query(None, ge=2000, le=2100, description="Filter by year (e.g., 2024)"),
    month: int = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    medium: str = Query(
        None, 
        regex="^(Instagram|WhatsApp|Twitter|Facebook|Other)$", 
        description="Filter by medium (Instagram, WhatsApp, Twitter, Facebook, Other)"
    )
):
    data = load_data()
    detections = filter_detections(data, year, month, None, None, medium)
    type_counts = {}

    for detection in detections:
        if detection["status"] == "Fake":
            # Extract the deepfake type from details
            details = detection["details"]
            # Extract deepfake type from details using reverse mapping
            deepfake_type = next((k for k, v in data["deepfake_types"].items() if v == details), "Other")
            type_counts[deepfake_type] = type_counts.get(deepfake_type, 0) + 1

    # Convert to lists
    types = list(type_counts.keys())
    counts = list(type_counts.values())
    return {"types": types, "counts": counts}



    
@app.get("/api/generate_report")
async def generate_report(
    format: str = Query("csv", regex="^(csv|pdf)$", description="Format of the report: csv or pdf"),
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
    ),
    medium: str = Query(
        None, 
        regex="^(Instagram|WhatsApp|Twitter|Facebook|Other)$", 
        description="Filter by medium (Instagram, WhatsApp, Twitter, Facebook, Other)"
    )
):
    data = load_data()
    filtered = filter_detections(data, year, month, media_type, status, medium)
    
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


@app.get("/api/medium_distribution")
async def get_medium_distribution(
    year: int = Query(None, ge=2000, le=2100, description="Filter by year (e.g., 2024)"),
    month: int = Query(None, ge=1, le=12, description="Filter by month (1-12)")
):
    data = load_data()
    filtered = filter_detections(data, year, month)
    medium_counts = {}
    for d in filtered:
        medium = d.get("medium", "Other")
        if d["status"] == "Fake":
            medium_counts[medium] = medium_counts.get(medium, 0) + 1
    # Convert to lists
    types = list(medium_counts.keys())
    counts = list(medium_counts.values())
    return {"types": types, "counts": counts}
