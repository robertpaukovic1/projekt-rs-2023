from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Scenarist   
from pydantic import BaseModel
from typing import List
from datetime import date 
import httpx  

def funckcija_server1():
    from glumci import GlumacPydantic   

def funkcija_server2():
    from redatelji import RedateljPydantic    

def funkcija_server5():
    from filmovi import FilmPydantic 

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


#Funkcije uvoza Pydantic modela različitih servera koje spriječavaju kružni uvoz

def import_GlumacPydantic():
    from glumci import GlumacPydantic
    return GlumacPydantic  

def import_RedateljPydantic():
    from redatelji import RedateljPydantic 
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
@app.post("/api/scenaristi/", status_code=status.HTTP_201_CREATED)
async def stvori_scenarista(scenarist: ScenaristCreate, db: Session = Depends(get_db)):
    print(scenarist.dict())
    db_scenarist = Scenarist(**scenarist.dict())
    db.add(db_scenarist)
    db.flush()  
    db.commit()
    db.refresh(db_scenarist)
    return {"msg": "Scenarist je evidentiran!"}  




#HTTP PUT izmjena email-a i telefonskog kontakta za scenarista 

@app.put("/api/novi-scenarist/{s_id}", status_code=status.HTTP_200_OK)
async def izmijeni_email_telefon_redatelja(s_id: str, novi_podaci: ScenaristCreate, db: Session = Depends(get_db)):
    db_scenarist = db.query(Scenarist).filter(Scenarist.s_id == s_id).first()

    if db_scenarist is None:
        raise HTTPException(status_code=404, detail="Scenarist nije pronađen")
    # Ažuriranje emaila i telefona
    db_scenarist.s_email = novi_podaci.s_email
    db_scenarist.s_telefon = novi_podaci.s_telefon
    db.commit()
    db.refresh(db_scenarist)
    return {"msg": "Scenarist je ažuriran"} 



# HTTP GET Dohvaćanje svih scenarista
@app.get("/api/scenaristi/", response_model=List[ScenaristPydantic], status_code=status.HTTP_200_OK)
async def dohvati_sve_scenariste(db: Session = Depends(get_db)):
    scenaristi = db.query(Scenarist).all()
    return scenaristi 



# HTTP GET Dohvaćanje jednog scenarista
@app.get("/api/scenarist/{s_id}", response_model=ScenaristPydantic)
async def dohvati_scenarista(s_id: str, db: Session = Depends(get_db)):
    scenarist = db.query(Scenarist).filter(Scenarist.s_id == s_id).first()
    if scenarist is None:
        raise HTTPException(status_code=404, detail="Scenarist nije pronađen")
    return scenarist


# HTTP GET dohvat glumaca sa prvog servera    

@app.get("/api/scenaristi_ka_glumcima/", response_model=List[GlumacPydantic], status_code=status.HTTP_200_OK)
async def dohvat_glumaca():
    glumci_url = "http://127.0.0.1:8000/api/glumci/"  
    try:
        with httpx.Client() as client:
            response =  client.get(glumci_url)
            response.raise_for_status() 
        glumci = response.json()
        return glumci
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju glumca sa prvog servera: {e}")



#HTTP GET dohvat redatelja sa drugog servera 

@app.get("/api/scenaristi_ka_redateljima", response_model=List[RedateljPydantic], status_code=status.HTTP_200_OK)
async def dohvat_redatelja():
    redatelji_url = "http://127.0.0.1:8001/api/redatelji/"  
    try:
        with httpx.Client() as client:
            response = client.get(redatelji_url)
            response.raise_for_status()  
        redatelji = response.json()
        return redatelji
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju redatelja sa drugog servera: {e}")



# HTTP GET Dohvat filmova sa petog servera 

@app.get("/api/scenarij_za_film/", response_model=List[FilmPydantic], status_code=status.HTTP_200_OK)
async def dohvat_filmova():
    filmovi_url = "http://127.0.0.1:8003/api/filmovi/"  
    try:
        with httpx.Client() as client:
            response =  client.get(filmovi_url)
            response.raise_for_status() 
        filmovi = response.json()
        return filmovi
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju filma sa petog servera: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
