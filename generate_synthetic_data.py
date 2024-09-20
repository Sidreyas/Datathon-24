import json
import random
from datetime import datetime, timedelta

# Configuration
NUM_ENTRIES = 500
OUTPUT_FILE = 'data/sample_data.json'
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2024, 9, 20)

MEDIA_TYPES = ["Video", "Audio", "Image"]
STATUSES = ["Real", "Fake"]
DEEPFAKE_TYPES = [
    "Face Swap",
    "Voice Synthesis",
    "Expression Manipulation",
    "Background Alteration",
    "Lip-sync Mismatch",
    "Object Insertion",
    "Scene Transition",
    "Voice Cloning",
    "Color Grading Inconsistency",
    "Echo Effect Manipulation"
]
DETAILS_MAPPING = {
    "Face Swap": "Face swap detected.",
    "Voice Synthesis": "Voice synthesis detected.",
    "Expression Manipulation": "Expression manipulation detected.",
    "Background Alteration": "Background alteration detected.",
    "Lip-sync Mismatch": "Lip-sync mismatch detected.",
    "Object Insertion": "Object insertion detected.",
    "Scene Transition": "Scene transition manipulation detected.",
    "Voice Cloning": "Voice cloning detected.",
    "Color Grading Inconsistency": "Color grading inconsistency detected.",
    "Echo Effect Manipulation": "Echo effect manipulation detected."
}

def random_date(start, end):
    """Generate a random datetime between `start` and `end`."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

def load_existing_data(file_path):
    """Load existing data from the JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def save_data(file_path, data):
    """Save updated data back to the JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def generate_detections(num_entries, start_date, end_date):
    """Generate synthetic detection entries."""
    detections = []
    current_id = 1
    for entry in data["recent_detections"]:
        if entry["id"] >= current_id:
            current_id = entry["id"] + 1
    for _ in range(num_entries):
        media_type = random.choice(MEDIA_TYPES)
        status = random.choice(STATUSES)
        if status == "Fake":
            deepfake_type = random.choice(DEEPFAKE_TYPES)
            details = DETAILS_MAPPING.get(deepfake_type, "Deepfake manipulation detected.")
        else:
            deepfake_type = "None"
            details = "No manipulation detected."
        
        timestamp = random_date(start_date, end_date).strftime("%Y-%m-%d %H:%M")
        confidence_score = round(random.uniform(0.75, 0.99), 2) if status == "Fake" else round(random.uniform(0.60, 0.85), 2)
        
        detection = {
            "id": current_id,
            "media_type": media_type,
            "timestamp": timestamp,
            "status": status,
            "confidence_score": confidence_score,
            "details": details
        }
        detections.append(detection)
        current_id += 1
    return detections

def update_overview(data):
    """Update the overview metrics based on recent detections."""
    total_media_processed = len(data["recent_detections"])
    total_deepfakes_detected = sum(1 for d in data["recent_detections"] if d["status"] == "Fake")
    detection_accuracy = round((total_deepfakes_detected / total_media_processed) * 100, 2) if total_media_processed else 0
    false_positives = sum(1 for d in data["recent_detections"] if d["status"] == "Fake" and d["confidence_score"] < 0.80)
    false_negatives = sum(1 for d in data["recent_detections"] if d["status"] == "Real" and d["confidence_score"] >= 0.80)
    
    data["overview"] = {
        "total_media_processed": total_media_processed,
        "total_deepfakes_detected": total_deepfakes_detected,
        "detection_accuracy": detection_accuracy,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }

def update_trend_data(data):
    """Update the trend data based on recent detections."""
    # Reset trend_data
    data["trend_data"] = {
        "dates": [],
        "detections": []
    }
    
    # Define the date range for trend_data
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 9, 20)
    delta = end_date - start_date
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        count = sum(1 for d in data["recent_detections"] if d["timestamp"].startswith(date_str))
        data["trend_data"]["dates"].append(date_str)
        data["trend_data"]["detections"].append(count)

def update_deepfake_types(data):
    """Update the deepfake types distribution based on recent detections."""
    type_counts = {}
    for d in data["recent_detections"]:
        if d["status"] == "Fake":
            # Extract the deepfake type from details
            details = d["details"]
            deepfake_type = next((k for k, v in DETAILS_MAPPING.items() if v == details), "Other")
            type_counts[deepfake_type] = type_counts.get(deepfake_type, 0) + 1
    # Convert to lists
    types = list(type_counts.keys())
    counts = list(type_counts.values())
    data["deepfake_types"] = {
        "types": types,
        "counts": counts
    }

if __name__ == "__main__":
    # Load existing data
    data = load_existing_data(OUTPUT_FILE)
    
    # Generate synthetic detections
    new_detections = generate_detections(NUM_ENTRIES, START_DATE, END_DATE)
    
    # Append to existing detections
    data["recent_detections"].extend(new_detections)
    
    # Update overview metrics
    update_overview(data)
    
    # Update trend data
    update_trend_data(data)
    
    # Update deepfake types
    update_deepfake_types(data)
    
    # Save the updated data back to the JSON file
    save_data(OUTPUT_FILE, data)
    
    print(f"Successfully added {NUM_ENTRIES} synthetic detections to '{OUTPUT_FILE}'.")
