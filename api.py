from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from aqua import mock_data, pipeline
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="AquaSentinel API")

# Allow CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data" / "pendrive"

@app.get("/api/results")
def get_results():
    if not (DATA_DIR / "readings.csv").exists():
        mock_data.generate_pendrive(DATA_DIR, per_class=3)
    results = pipeline.process_pendrive(DATA_DIR)
    
    clean_results = []
    for r in results:
        r_clean = dict(r)
        img_path = Path(r["image_path"])
        r_clean["image_url"] = f"http://localhost:8000/images/{img_path.name}"
        clean_results.append(r_clean)
        
    return {"results": clean_results}

if not DATA_DIR.exists():
    mock_data.generate_pendrive(DATA_DIR, per_class=3)
images_dir = DATA_DIR / "images"
if images_dir.exists():
    app.mount("/images", StaticFiles(directory=str(images_dir)), name="images")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
