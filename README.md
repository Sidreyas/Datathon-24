# Deepfake Detection & Mitigation System

### Frontend

The system's user interface is built with React JS, Tailwind CSS, and Vite. 

## Backend

A Flask API handles all processing requests, including model inference and data storage.

### Deepfake Detection

The core of the system is a deepfake detection model trained on various datasets with Federated learning. It utilizes ResNet, Inception, and Vision-Transformer architectures.

### Databases

Two databases store the system's data: MongoDB for media files and MySQL for user information and reports.

### Model Efficiency

Post-Training Quantization is applied for faster inference, while GPU utilization optimizes performance.

## Accuracy 

98.64% with 15ms-20ms inference time
