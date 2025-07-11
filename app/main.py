from fastapi import FastAPI,BackgroundTasks,HTTPException,Request,Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app import schemas, crud, models
from app.database import get_db, engine,SessionLocal
from app.utily import perform_translation
from typing import List
import uuid

models.Base.metadata.create_all(bind=engine)

app=FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials = True,
    allow_methods=["*"], # Allows al methods
    allow_headers=["*"], # Allows all headers
)

# Enable CORS
# docker compose up --build
# docker exec -it translation_postgres psql -U myuser -d translationdb
# \dt
# SELECT * FROM translation_tasks;
# \q

@app.get('/index',response_class=HTMLResponse)
def index(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.post('/translate',response_model=schemas.TaskResponse)
def translate(request: schemas.TranslationRequest,background_tasks:BackgroundTasks, db:Session=Depends(get_db)):
    task = crud.create_translation_task(db,request.text,request.languages)
    background_tasks.add_task(perform_translation, task.id,request.text, request.languages,db)
    return {"task_id":task.id}

@app.get('/translate/{task_id}',response_model=schemas.TranslationStatus)
def get_translate(task_id:int,db:Session=Depends(get_db)):
    task = crud.get_translation_task(db,task_id)
    if not task:
        raise HTTPException(status_code=404,detail="task not found")
    translations = task.translations if task.translations is not None else {}
    return {
        "task_id":task.id,
        "status": task.status,
        "translation":translations
    }

@app.get("/translate/content/{task_id}")
def get_translate_content(task_id:int,db:Session=Depends(get_db)):
    task = crud.get_translation_task(db,task_id)
    if not task:
        raise HTTPException(status_code=404,detail="task not found")
    return task