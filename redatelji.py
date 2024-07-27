from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Redatelj  
from pydantic import BaseModel
from typing import List
from datetime import date 
import httpx  

def funckcija_server1():
    from glumci import GlumacPydantic    

from scenaristi import ScenaristPydantic   
from filmovi import FilmPydantic 

app = FastAPI()

# Pydantic model za redatelja
class RedateljPydantic(BaseModel):
    r_id: str
    r_ime: str
    r_prezime: str
    r_datum_rodjenja: date
    r_email: str
    r_telefon: int
    r_karijera_pocetak: date
    r_karijera_kraj: date
    r_nagrade: str  

# Dohvaćanje sheme baze za redatelje
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RedateljBase(BaseModel):
    r_id: str
    r_ime: str
    r_prezime: str
    r_datum_rodjenja: date
    r_email: str
    r_telefon: int
    r_karijera_pocetak: date
    r_karijera_kraj: date
    r_nagrade: str

class RedateljCreate(RedateljBase):
    pass    

#Pydantic modeli sa vanjskih servera 

class GlumacPydantic(BaseModel):
   g_id: str  
   g_ime: str  
   g_prezime: str 
   g_datum_rodjenja: date   
   g_mjesto_rodjenja: str  
   g_nacionalnost: str  
   g_nagrade:str  


#Funkcije uvoza Pydantic modela različitih servera koje spriječavaju kružni uvoz

def import_GlumacPydantic():
    from glumci import GlumacPydantic
    return GlumacPydantic  


# HTTP POST Evidencija novih filmskih redatelja
@app.post("/redatelji/", status_code=status.HTTP_201_CREATED)
async def stvori_redatelja(redatelj: RedateljCreate, db: Session = Depends(get_db)):
    print(redatelj.dict())
    db_redatelj = Redatelj(**redatelj.dict())
    db.add(db_redatelj)
    db.flush()  
    db.commit()
    db.refresh(db_redatelj)
    return {"msg": "Redatelj je evidentiran!"}

# HTTP GET Dohvaćanje svih redatelja
@app.get("/redatelji/", response_model=List[RedateljPydantic], status_code=status.HTTP_200_OK)
async def dohvati_sve_redatelje(db: Session = Depends(get_db)):
    redatelji = db.query(Redatelj).all()
    return redatelji

# HTTP GET Dohvaćanje jednog redatelja
@app.get("/redatelj/{r_id}", response_model=RedateljPydantic)
async def dohvati_redatelja(r_id: str, db: Session = Depends(get_db)):
    redatelj = db.query(Redatelj).filter(Redatelj.r_id == r_id).first()
    if redatelj is None:
        raise HTTPException(status_code=404, detail="Redatelj nije pronađen")
    return redatelj   

#HTTP PUT izmjena email i telefon kontakta za trećeg redatelja  

@app.put("/novi-redatelj/{r_id}", status_code=status.HTTP_200_OK)
async def izmijeni_email_telefon_redatelja(r_id: str, novi_podaci: RedateljCreate, db: Session = Depends(get_db)):
    db_redatelj = db.query(Redatelj).filter(Redatelj.r_id == r_id).first()

    if db_redatelj is None:
        raise HTTPException(status_code=404, detail="Redatelj nije pronađen")

    # Ažuriranje emaila i telefona
    db_redatelj.r_email = novi_podaci.r_email
    db_redatelj.r_telefon = novi_podaci.r_telefon

    db.commit()
    db.refresh(db_redatelj)

    return {"msg": "Email i telefon redatelja su ažurirani"}    

#HTTP GET Dohvat glumaca sa prvog servera   

@app.get("/redatelji_ka_glumcima/", response_model=List[GlumacPydantic], status_code=status.HTTP_200_OK)
async def dohvati_glumaca():
    glumci_url = "http://127.0.0.1:8000/glumci/"  
    try:
        with httpx.Client() as client:
            response = client.get(glumci_url)
            response.raise_for_status()  
        glumci = response.json()
        return glumci
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju glumca sa prvog servera: {e}")

# HTTP GET Dohvat scenarista sa trećeg servera 

@app.get("/dohvat-scenarista-sa-servera-scenaristi/", response_model=List[ScenaristPydantic], status_code=status.HTTP_200_OK)
async def dohvati_scenarista_sa_treceg_servera():
    SERVER3_BASE_URL = "http://127.0.0.1:8002"  
    scenaristi_url = f"{SERVER3_BASE_URL}/scenaristi/"
    
    try:
        # Izvršavanje HTTP GET zahtjeva prema trecem serveru
        with httpx.Client() as client:
            response = client.get(scenaristi_url)
            response.raise_for_status()  # Podiže iznimku ako je status kod odgovora neuspješan

        # Pretvorba odgovora u listu scenarista
        scenaristi = response.json()
        return scenaristi
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju scenarista sa trećeg servera: {e}")


# HTTP GET Dohvat filmova sa petog servera 

@app.get("/dohvat-filmova-sa-servera-filmovi/", response_model=List[FilmPydantic], status_code=status.HTTP_200_OK)
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
    uvicorn.run(app, host="0.0.0.0", port=8001)






