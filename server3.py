from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Scenarist  
from pydantic import BaseModel
from typing import List
from datetime import date 
import httpx  

def funckcija_server1():
    from server1 import GlumacPydantic   

def funkcija_server2():
    from server2 import RedateljPydantic    

from server5 import FilmPydantic 

app = FastAPI()

# Pydantic model za scenarista
class ScenaristPydantic(BaseModel):
    s_id: str
    s_ime: str
    s_prezime: str
    s_datum_rodjenja: date
    s_email: str
    s_telefon: int
    s_karijera_pocetak: date
    s_karijera_kraj: date
    s_nagrade: str  


# Pydantic modeli od servera1 i servera 2

class GlumacPydantic(BaseModel):
   g_id: str  
   g_ime: str  
   g_prezime: str 
   g_datum_rodjenja: date   
   g_mjesto_rodjenja: str  
   g_nacionalnost: str  
   g_nagrade:str   

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


#Funkcije uvoza Pydantic modela različitih servera koje spriječavaju kružni uvoz

def import_GlumacPydantic():
    from server1 import GlumacPydantic
    return GlumacPydantic  

def import_RedateljPydantic():
    from server2 import RedateljPydantic 
    return RedateljPydantic

# Dohvaćanje sheme baze za scenariste
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# HTTP POST Unos podataka o novom scenaristu 
class ScenaristBase(BaseModel):
    s_id: str
    s_ime: str
    s_prezime: str
    s_datum_rodjenja: date
    s_email: str
    s_telefon: int
    s_karijera_pocetak: date
    s_karijera_kraj: date
    s_nagrade: str

class ScenaristCreate(ScenaristBase):
    pass

# HTTP POST Evidencija novih filmskih scenarista
@app.post("/scenaristi/", status_code=status.HTTP_201_CREATED)
async def stvori_scenarista(scenarist: ScenaristCreate, db: Session = Depends(get_db)):
    print(scenarist.dict())
    db_scenarist = Scenarist(**scenarist.dict())
    db.add(db_scenarist)
    db.flush()  
    db.commit()
    db.refresh(db_scenarist)
    return {"msg": "Scenarist je evidentiran!"}

# HTTP GET Dohvaćanje svih scenarista
@app.get("/scenaristi/", response_model=List[ScenaristPydantic], status_code=status.HTTP_200_OK)
async def dohvati_sve_scenariste(db: Session = Depends(get_db)):
    scenaristi = db.query(Scenarist).all()
    return scenaristi 

# HTTP GET Dohvaćanje jednog scenarista
@app.get("/scenarist/{s_id}", response_model=ScenaristPydantic)
async def dohvati_scenarista(s_id: str, db: Session = Depends(get_db)):
    scenarist = db.query(Scenarist).filter(Scenarist.s_id == s_id).first()
    if scenarist is None:
        raise HTTPException(status_code=404, detail="Scenarist nije pronađen")
    return scenarist

#HTTP POST evidencija novog scenarista te slanje rješenja prvom serveru 
@app.post("/scenarist-k-prvom/", status_code=status.HTTP_201_CREATED)
async def stvori_scenarista(scenarist: ScenaristCreate):
    prvi_server_url = "http://localhost:8000/primi-rjesenje-iz-treceg-servera/"
    try:
        with httpx.AsyncClient() as client:
            response = await client.post(prvi_server_url, json=scenarist.dict())
            response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri slanju rješenja prvom serveru: {e}")

    return {"msg": "Scenarist je evidentiran i rješenje poslano prvom serveru!"}  

# HTTP GET dohvat glumaca sa prvog servera    

@app.get("/dohvati-glumce-sa-prvog-servera/", response_model=List[GlumacPydantic], status_code=status.HTTP_200_OK)
async def dohvati_glumce_sa_prvog_servera():
    SERVER1_BASE_URL = "http://127.0.0.1:8000"  
    glumci_url = f"{SERVER1_BASE_URL}/glumci/"
    
    try:
        # Izvršavanje HTTP GET zahtjeva prema drugom serveru
        with httpx.Client() as client:
            response = client.get(glumci_url)
            response.raise_for_status()  # Podiže iznimku ako je status kod odgovora neuspješan

        # Pretvorba odgovora u listu redatelja
        glumci = response.json()
        return glumci
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju glumca sa prvog servera: {e}")


#HTTP GET dohvat redatelja sa drugog servera 

@app.get("/dohvati-redatelje-sa-drugog-servera/", response_model=List[RedateljPydantic], status_code=status.HTTP_200_OK)
async def dohvati_redatelje_sa_drugog_servera():
    SERVER2_BASE_URL = "http://127.0.0.1:8001"  
    redatelji_url = f"{SERVER2_BASE_URL}/redatelji/"
    
    try:
        # Izvršavanje HTTP GET zahtjeva prema drugom serveru
        with httpx.Client() as client:
            response = client.get(redatelji_url)
            response.raise_for_status()  # Podiže iznimku ako je status kod odgovora neuspješan

        # Pretvorba odgovora u listu redatelja
        redatelji = response.json()
        return redatelji
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju redatelja sa drugog servera: {e}")


# HTTP GET Dohvat filmova sa petog servera 

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
    uvicorn.run(app, host="0.0.0.0", port=8002)
