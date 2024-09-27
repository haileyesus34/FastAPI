from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse  # Import FileResponse
import os
import cv2
from pathlib import Path
import aiofiles
import shutil

app = FastAPI()

UPLOAD_DIR = Path("./videos/uploaded")
PROCESSED_DIR = Path("./videos/processed")

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    video_path = UPLOAD_DIR / file.filename
    
    # Save uploaded video
    async with aiofiles.open(video_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Process the video (e.g., extract frames)
    processed_video_path = process_video(video_path, file.filename)
    
    return {"message": "Video uploaded and processed", "processed_video": str(processed_video_path)}

def process_video(video_path: Path, filename: str) -> Path:
    # Read the video using OpenCV
    cap = cv2.VideoCapture(str(video_path))
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Create processed video path
    output_path = PROCESSED_DIR / f"processed_{filename}"
    
    # Define video codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (frame_width, frame_height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process the frame (e.g., convert to grayscale)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        out.write(cv2.merge([gray_frame, gray_frame, gray_frame]))  # Save grayscale frames
    
    cap.release()
    out.release()
    
    return output_path

@app.get("/videos/{video_name}")
async def get_video(video_name: str):
    video_path = PROCESSED_DIR / video_name
    if video_path.exists():
        return FileResponse(video_path)
    else:
        return {"error": "Video not found"}
