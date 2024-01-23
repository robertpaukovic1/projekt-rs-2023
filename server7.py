from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Ocjena 
from datetime import date  
from pydantic import BaseModel
from typing import List  
import httpx

app = FastAPI()  

def funckcija_server1():
    from server1 import GlumacPydantic   
 

# Pydantic model za uloge
class OcjenaPydantic(BaseModel):
    m_id: int 
    f_id: int  
    ocjena: float 
    komentar: str 
    datum_ocjenjivanja:date

#Funkcije uvoza Pydantic modela različitih servera koje spriječavaju kružni uvoz

def import_FilmPydantic():
    from server5 import FilmPydantic
    return FilmPydantic

# Dohvaćanje sheme baze za uloge
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Model unosa podataka o pripadajućol ulozi glumca u tom filmu
class OcjenaBase(BaseModel):
    m_id: int 
    f_id: int  
    ocjena: float 
    komentar: str 
    datum_ocjenjivanja:date

class OcjenaCreate(OcjenaBase):
    pass   


#Pydantic modeli sa prvog i petog servera  

class FilmPydantic(BaseModel): 
    f_id:int
    f_naslov:str
    f_godina:int 
    f_zanr: str  
    f_trajanje_u_minutama: int
    r_id: str
    s_id : str   
    st_id: int


# HTTP POST Evidencija prve ocjene na pogledani film
@app.post("/prva_ocjena/", status_code=status.HTTP_201_CREATED)
async def upis_ocjene(ocjena: OcjenaCreate, db: Session = Depends(get_db)):
    print(ocjena.dict())
    db_ocjena = Ocjena(**ocjena.dict())
    db.add(db_ocjena)
    db.flush()  
    db.commit()
    db.refresh(db_ocjena)
    return {"msg": "Ocjena filmu je dodijeljena"}

# HTTP GET Dohvaćanje svih ocjenjenih filmova
@app.get("/ocjene/", response_model=List[OcjenaPydantic], status_code=status.HTTP_200_OK)
async def dohvati_sve_ocjene(db: Session = Depends(get_db)):
    ocjene = db.query(Ocjena).all()
    return ocjene

# HTTP GET Dohvaćanje jedne filmske uloge
@app.get("/ocjena/{m_id}", response_model=OcjenaPydantic)
async def dohvati_ocjenu(m_id: int, db: Session = Depends(get_db)):
    ocjena= db.query(Ocjena).filter(Ocjena.m_id == m_id).first()
    if ocjena is None:
        raise HTTPException(status_code=404, detail="Ocjena pripadajucem filmu ne postoji")
    return ocjena  


#HTTP GET dohvat filma sa sa petog servera  

@app.get("/dohvati-filmove-sa-petog-servera/", response_model=List[FilmPydantic], status_code=status.HTTP_200_OK)
async def dohvati_filmove_sa_petog_servera():
    SERVER5_BASE_URL = "http://127.0.0.1:8003"  
    filmovi_url = f"{SERVER5_BASE_URL}/filmovi/"
    
    try:
        # Izvršavanje HTTP GET zahtjeva prema trecem serveru
        with httpx.Client() as client:
            response = client.get(filmovi_url)
            response.raise_for_status()  # Podiže iznimku ako je status kod odgovora neuspješan

        # Pretvorba odgovora u listu scenarista
        filmovi = response.json()
        return filmovi
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju filma sa petog servera: {e}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)