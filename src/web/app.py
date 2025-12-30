from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.core.controller import DTMController
from typing import List
import os

app = FastAPI(title="DTM Dashboard")

# Determine templates directory relative to this file
current_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

def get_controller():
    # Helper to get controller instance (assuming we run from repo root or handle paths)
    # We might need to pass root_dir dynamically if not "."
    return DTMController(".")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    try:
        controller = get_controller()
        history = controller.log()
        return templates.TemplateResponse("index.html", {"request": request, "commits": history})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "commits": [], "error": str(e)})

@app.get("/commit/{commit_id}", response_class=HTMLResponse)
async def read_commit(request: Request, commit_id: str):
    try:
        controller = get_controller()
        commit = controller.metadata.get_commit(commit_id)
        return templates.TemplateResponse("commit.html", {"request": request, "commit": commit})
    except ValueError:
        raise HTTPException(status_code=404, detail="Commit not found")

@app.get("/diff/{commit_a}/{commit_b}", response_class=HTMLResponse)
async def read_diff(request: Request, commit_a: str, commit_b: str):
    try:
        controller = get_controller()
        diff_text = controller.diff(commit_a, commit_b)
        return templates.TemplateResponse("diff.html", {
            "request": request, 
            "diff": diff_text, 
            "commit_a": commit_a, 
            "commit_b": commit_b
        })
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
