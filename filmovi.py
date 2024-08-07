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
@app.post("/api/filmovi/", status_code=status.HTTP_201_CREATED)
async def stvori_film(film: FilmCreate, db: Session = Depends(get_db)):
    print(film.dict())
    db_film = Film(**film.dict())
    db.add(db_film)
    db.flush()  
    db.commit()
    db.refresh(db_film)
    return {"msg": "Film je evidentiran!"}



# HTTP GET Dohvaćanje svih filmova
@app.get("/api/filmovi/", response_model=List[FilmPydantic], status_code=status.HTTP_200_OK)
async def dohvati_sve_filmove(db: Session = Depends(get_db)):
    filmovi = db.query(Film).all()
    return filmovi 



# HTTP GET Dohvaćanje jednog filma
@app.get("/api/film/{f_id}", response_model=FilmPydantic)
async def dohvati_film(f_id: int, db: Session = Depends(get_db)):
    film = db.query(Film).filter(Film.f_id == f_id).first()
    if film is None:
        raise HTTPException(status_code=404, detail="Trazeni film nije pronađen")
    return film    



# HTTP PUT Izmjena minute trajanja filma

@app.put("/api/film/{f_id}", response_model=FilmPydantic)
async def izmijeni_trajanje_filma(f_id: int, update_data: FilmUpdate, db: Session = Depends(get_db)):
    film = get_film_by_id(db, f_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Traženi film nije pronađen")
    film.f_trajanje_u_minutama = update_data.f_trajanje_u_minutama
    db.commit()

    return film



#  HTTP dohvat redatelja sa drugog servera  

@app.get("/api/pripadajuci_redatelji/", response_model=List[RedateljPydantic], status_code=status.HTTP_200_OK)
async def dohvat_redatelja():
    redatelji_url = "http://127.0.0.1:8001/api/redatelji/"  
    try:
        with httpx.Client() as client:
            response =  client.get(redatelji_url)
            response.raise_for_status()  
        redatelji = response.json()
        return redatelji
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju redatelja sa drugog servera: {e}")




# HTTP GET dohvat scenarista sa trećeg servera

@app.get("/api/zasluzni_scenaristi/", response_model=List[ScenaristPydantic], status_code=status.HTTP_200_OK)
async def dohvat_scenarista():
    scenaristi_url = "http://127.0.0.1:8002/api/scenaristi/"  
    try:
        with httpx.Client() as client:
            response = client.get(scenaristi_url)
            response.raise_for_status()  
        scenaristi = response.json()
        return scenaristi
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju scenarista sa trećeg servera: {e}")




# HTTP GET Dohvat filmskog studija sa četvrtog servera 
    
@app.get("/api/filmski_studio/", response_model=List[StudioPydantic], status_code=status.HTTP_200_OK)
async def dohvat_filmskih_studija():
    studios_url = "http://127.0.0.1:8004/api/studio-s/"  
    try:
        with httpx.Client() as client:
            response = client.get(studios_url)
            response.raise_for_status()   
        studios = response.json()
        return studios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju filmskog studija sa četvrtog servera: {e}")





# HTTP GET dohvat filmskih uloga sa šestog servera 


@app.get("/api/glumacke_uloge/", response_model=List[UlogaPydantic], status_code=status.HTTP_200_OK)
async def dohvat_filmske_uloge_sa_sestog_servera():
    uloge_url = "http://127.0.0.1:8005/api/uloge/"  
    try:
        with httpx.Client() as client:
            response =  client.get(uloge_url)
            response.raise_for_status()  
        uloge = response.json()
        return uloge
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju filmskih uloga sa šestog servera: {e}") 
    


# HTTP GET dohvat ocjene gledanosti pojedinih filmova sa sedmog servera 


@app.get("/api/ocjena_gledanosti_za_film/", response_model=List[OcjenaPydantic], status_code=status.HTTP_200_OK)
async def dohvat_ocjene_gledanosti():
    ocjene_url = "http://127.0.0.1:8006/api/ocjene/"  
    try:
        with httpx.Client() as client:
            response =  client.get(ocjene_url)
            response.raise_for_status() 
        ocjene = response.json()
        return ocjene
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju ocjenjenih filmova sa sedmog servera: {e}") 
    



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)