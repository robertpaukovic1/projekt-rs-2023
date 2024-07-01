from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Film  
from pydantic import BaseModel
from typing import List
from datetime import date 
import httpx  
   
from uloge import UlogaPydantic    
from ocjene import OcjenaPydantic  
from scenaristi import ScenaristPydantic

app = FastAPI()

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

# Dohvaćanje sheme baze za filmove
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# HTTP POST Unos podataka o novom filmu
class FilmBase(BaseModel): 
    f_id:int
    f_naslov:str
    f_godina:int 
    f_zanr: str  
    f_trajanje_u_minutama: int
    r_id: str
    s_id : str   
    st_id: int   

class FilmCreate(FilmBase):
    pass   

#Pydantic modeli scenarista i redatelja  

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



#Pydantic model za filmski studio  
    
class StudioPydantic(BaseModel):
    st_id: int 
    st_naziv: str
    st_godina_osnutka:int   

#Pydantic model za filmsku ulogu   
    
class UlogaPydantic(BaseModel):
    u_id: int 
    f_id: int  
    g_id: str 
    uloga: str 
    tip_uloge:str   

#Pydantic model za izmjenu minute filma 
 
class FilmUpdate(BaseModel):
    f_trajanje_u_minutama: int

#Funkcije uvoza Pydantic modela različitih servera koje spriječavaju kružni uvoz

def import_RedateljPydantic():
    from redatelji import RedateljPydantic
    return RedateljPydantic  

def import_ScenaristPydantic():
    from scenaristi import ScenaristPydantic 
    return ScenaristPydantic  

def import_StudioPydantic():
    from studio import StudioPydantic 
    return StudioPydantic   

def import_UlogaPydantic():
    from uloge import UlogaPydantic 
    return UlogaPydantic


#Funkcije dohvata filma po ID-u

def get_film_by_id(db: Session, film_id: int):
    return db.query(Film).filter(Film.f_id == film_id).first()

# HTTP POST Evidencija novog filma 
@app.post("/filmovi/", status_code=status.HTTP_201_CREATED)
async def stvori_film(film: FilmCreate, db: Session = Depends(get_db)):
    print(film.dict())
    db_film = Film(**film.dict())
    db.add(db_film)
    db.flush()  
    db.commit()
    db.refresh(db_film)
    return {"msg": "Film je evidentiran!"}

# HTTP GET Dohvaćanje svih filmova
@app.get("/filmovi/", response_model=List[FilmPydantic], status_code=status.HTTP_200_OK)
async def dohvati_sve_filmove(db: Session = Depends(get_db)):
    filmovi = db.query(Film).all()
    return filmovi 

# HTTP GET Dohvaćanje jednog filma
@app.get("/film/{f_id}", response_model=FilmPydantic)
async def dohvati_film(f_id: int, db: Session = Depends(get_db)):
    film = db.query(Film).filter(Film.f_id == f_id).first()
    if film is None:
        raise HTTPException(status_code=404, detail="Trazeni film nije pronađen")
    return film    

# HTTP PUT Izmjena minute trajanja filma

@app.put("/film/{f_id}", response_model=FilmPydantic)
async def izmijeni_trajanje_filma(f_id: int, update_data: FilmUpdate, db: Session = Depends(get_db)):
    # Check if the film with the given ID exists
    film = get_film_by_id(db, f_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Traženi film nije pronađen")

    # Update only the duration field
    film.f_trajanje_u_minutama = update_data.f_trajanje_u_minutama
    db.commit()

    return film

#HTTP POST evidencija novog filma te slanje rješenja prvom serveru 

@app.post("/film-k-prvom/", status_code=status.HTTP_201_CREATED)
async def stvori_film2(film: FilmCreate):
    prvi_server_url = "http://localhost:8000/primi-rjesenje-iz-petog-servera/"
    try:
        with httpx.AsyncClient() as client:
            response = await client.post(prvi_server_url, json=film.dict())
            response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri slanju rješenja prvom serveru: {e}")

    return {"msg": "Film je evidentiran i rješenje poslano prvom serveru!"}


#  HTTP dohvat redatelja sa drugog servera  

@app.get("/dohvat-redatelja-sa-servera-redatelji/", response_model=List[RedateljPydantic], status_code=status.HTTP_200_OK)
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


# HTTP GET dohvat scenarista sa trećeg servera

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


# HTTP GET Dohvat filmskog studija sa četvrtog servera 
    
@app.get("/dohvat-filmskih-studija-sa-servera-studio/", response_model=List[StudioPydantic], status_code=status.HTTP_200_OK)
async def dohvati_filmska_studia_sa_cetvrtog_servera():
    SERVER4_BASE_URL = "http://127.0.0.1:8004"  
    studios_url = f"{SERVER4_BASE_URL}/studio-s/"
    
    try:
        # Izvršavanje HTTP GET zahtjeva prema četvrtom serveru
        with httpx.Client() as client:
            response = client.get(studios_url)
            response.raise_for_status()  # Podiže iznimku ako je status kod odgovora neuspješan

        # Pretvorba odgovora u listu filmskih studia 
        studios = response.json()
        return studios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju filmskog studija sa četvrtog servera: {e}")

# HTTP GET dohvat filmskih uloga sa šestog servera 


@app.get("/dohvat-filmskih-uloga-sa-servera-uloge/", response_model=List[UlogaPydantic], status_code=status.HTTP_200_OK)
async def dohvat_filmske_uloge_sa_sestog_servera():
    SERVER6_BASE_URL = "http://127.0.0.1:8005"  
    uloge_url = f"{SERVER6_BASE_URL}/uloge/"
    
    try:
        # Izvršavanje HTTP GET zahtjeva prema sestog serveru
        with httpx.Client() as client:
            response = client.get(uloge_url)
            response.raise_for_status()  # Podiže iznimku ako je status kod odgovora neuspješan

        # Pretvorba odgovora u listu uloga
        uloge = response.json()
        return uloge
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju filmskih uloga sa šestog servera: {e}") 
    

# HTTP GET dohvat ocjene gledanosti pojedinih filmova sa sedmog servera 


@app.get("/dohvat-ocjena-sa-sedmog-servera/", response_model=List[OcjenaPydantic], status_code=status.HTTP_200_OK)
async def dohvati_ocjene_sa_sedmog_servera():
    SERVER7_BASE_URL = "http://127.0.0.1:8006"  
    ocjene_url = f"{SERVER7_BASE_URL}/ocjene/"
    
    try:
        # Izvršavanje HTTP GET zahtjeva prema sedmom serveru
        with httpx.Client() as client:
            response = client.get(ocjene_url)
            response.raise_for_status()  # Podiže iznimku ako je status kod odgovora neuspješan

        # Pretvorba odgovora u listu uloga
        ocjene = response.json()
        return ocjene
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju ocjenjenih filmova sa sedmog servera: {e}") 
    



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)