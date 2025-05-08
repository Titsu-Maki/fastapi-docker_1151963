from fastapi import FastAPI, Request, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os

app = FastAPI()

#https://github.com/hyperdxio/fastapi-opentelemetry-example/blob/main/database.py
SQLALCHEMY_DATABASE_URL = "sqlite:///./db.sqlite"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {
        "message": "Welcome to the FastAPI application! "
        "You can use this API to manage your notes."
    }


@app.get("/notes")
async def get_notes(db: Session = Depends(get_db)):
    try:
        notes = db.query(Note).all()
        return {"notes": notes}
    
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error. Please try again later.")


@app.post("/notes")
async def create_note(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        raise HTTPException(status_code=400, detail="Title and content are required")

    try:
        new_note = Note(title=title, content=content)
        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        return {"message": "Nota creada", "note": {"title": new_note.title, "content": new_note.content}}

    #https://stackoverflow.com/questions/8870217/why-do-i-get-sqlalchemy-nested-rollback-error
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error en la database.")
