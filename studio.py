from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Studio  
from pydantic import BaseModel
from typing import List  
import httpx

app = FastAPI()  

from filmovi import FilmPydantic

# Pydantic model za studio
class StudioPydantic(BaseModel):
    st_id: int 
    st_naziv: str
    st_godina_osnutka:int 

# Pydantic model za filmove  
    
class FilmPydantic(BaseModel): 
    f_id:int
    f_naslov:str
    f_godina:int 
    f_zanr: str  
    f_trajanje_u_minutama: int
    r_id: str
    s_id : str   
    st_id: int

# Dohvaćanje sheme baze za filmski studio
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Model unosa podataka o novom fimskom studio-u
class StudioBase(BaseModel):
    st_id: int 
    st_naziv: str
    st_godina_osnutka:int

class StudioCreate(StudioBase):
    pass


# HTTP POST Evidencija novih filmskih studio-a
@app.post("/novi-studio/", status_code=status.HTTP_201_CREATED)
async def stvori_studio(studio: StudioCreate, db: Session = Depends(get_db)):
    print(studio.dict())
    db_studio = Studio(**studio.dict())
    db.add(db_studio)
    db.flush()  
    db.commit()
    db.refresh(db_studio)
    return {"msg": "Filmski studio je dodan!"}



# HTTP GET Dohvaćanje svih filsmkih studia
@app.get("/studio-s/", response_model=List[StudioPydantic], status_code=status.HTTP_200_OK)
async def dohvati_sva_studio_a(db: Session = Depends(get_db)):
    studios = db.query(Studio).all()
    return studios



# HTTP GET Dohvaćanje jednog filmskog studia
@app.get("/studio/{st_id}", response_model=StudioPydantic)
async def dohvati_studio(st_id: int, db: Session = Depends(get_db)):
    studio= db.query(Studio).filter(Studio.st_id == st_id).first()
    if studio is None:
        raise HTTPException(status_code=404, detail="Filmski studio nije pronadj")
    return studio  




#HTTP GET dohvat filma sa sa petog servera  

@app.get("/studio_za_film/", response_model=List[FilmPydantic], status_code=status.HTTP_200_OK)
async def dohvat_filmova():
    filmovi_url = "http://127.0.0.1:8003/filmovi/"  
    try:
        with httpx.Client() as client:
            response = client.get(filmovi_url)
            response.raise_for_status()  
        filmovi = response.json()
        return filmovi
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju filma sa petog servera: {e}")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)