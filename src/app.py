import os
from os.path import join, dirname
from dotenv import load_dotenv
import sys

# Print current working directory for debugging
print(f"Current working directory: {os.getcwd()}")

# Try to load environment variables
try:
    dotenv_path = join(dirname(__file__), "key.env")
    print(f"Loading environment from: {dotenv_path}")
    load_dotenv(dotenv_path)
    print(f"API key loaded: {'Yes' if os.getenv('SHODAN_API_KEY') else 'No'}")
    if os.getenv('SHODAN_API_KEY'):
        print(f"API key starts with: {os.getenv('SHODAN_API_KEY')[:5]}...")
except Exception as e:
    print(f"Error loading environment: {e}")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from src.routes.dashboard import router as dashboard_router

app = FastAPI()

# Set up the templates directory
templates = Jinja2Templates(directory=join(dirname(__file__), "templates"))

# Middleware to allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the dashboard routes (your API endpoints)
app.include_router(dashboard_router)

@app.get("/")
def read_root(request: Request):
    # Updated to return an HTML template instead of JSON
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard")
def view_dashboard(request: Request):
    # You can add data to pass into your template here
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)