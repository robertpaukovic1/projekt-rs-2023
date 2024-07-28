from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Uloga  
from datetime import date  
from pydantic import BaseModel
from typing import List  
import httpx

app = FastAPI()  

def funckcija_server1():
    from glumci import GlumacPydantic   
 

# Pydantic model za uloge
class UlogaPydantic(BaseModel):
    u_id: int 
    f_id: int  
    g_id: str 
    uloga: str 
    tip_uloge:str

#Funkcije uvoza Pydantic modela različitih servera koje spriječavaju kružni uvoz

def import_GlumacPydantic():
    from glumci import GlumacPydantic
    return GlumacPydantic

# Dohvaćanje sheme baze za uloge
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Model unosa podataka o pripadajućol ulozi glumca u tom filmu
class UlogaBase(BaseModel):
    u_id: int 
    f_id: int  
    g_id: str 
    uloga: str 
    tip_uloge:str

class UlogaCreate(UlogaBase):
    pass   


#Pydantic modeli sa prvog i petog servera  

class GlumacPydantic(BaseModel):
   g_id: str  
   g_ime: str  
   g_prezime: str 
   g_datum_rodjenja: date   
   g_mjesto_rodjenja: str  
   g_nacionalnost: str  
   g_nagrade:str

class FilmPydantic(BaseModel): 
    f_id:int
    f_naslov:str
    f_godina:int 
    f_zanr: str  
    f_trajanje_u_minutama: int
    r_id: str
    s_id : str   
    st_id: int


# HTTP POST Evidencija prvih filmskih uloga
@app.post("/nova-uloga/", status_code=status.HTTP_201_CREATED)
async def stvori_ulogu(uloga: UlogaCreate, db: Session = Depends(get_db)):
    print(uloga.dict())
    db_uloga = Uloga(**uloga.dict())
    db.add(db_uloga)
    db.flush()  
    db.commit()
    db.refresh(db_uloga)
    return {"msg": "Uloga glumcu je dodana!"}



# HTTP GET Dohvaćanje svih filsmkih glumačkih uloga 
@app.get("/uloge/", response_model=List[UlogaPydantic], status_code=status.HTTP_200_OK)
async def dohvati_sve_uloge(db: Session = Depends(get_db)):
    uloge = db.query(Uloga).all()
    return uloge



# HTTP GET Dohvaćanje jedne filmske uloge
@app.get("/uloga/{u_id}", response_model=UlogaPydantic)
async def dohvati_ulogu(u_id: int, db: Session = Depends(get_db)):
    uloga= db.query(Uloga).filter(Uloga.u_id == u_id).first()
    if uloga is None:
        raise HTTPException(status_code=404, detail="Pripadajuca uloga glumcu nije pronadjena")
    return uloga    



#HTTP PUT izmjena tipa uloge za glumca   

@app.put("/izmjena-tipa-uloge/{u_id}", status_code=status.HTTP_200_OK)
async def izmjena_tipa_uloge(u_id: int, novi_tip_uloge: str, db: Session = Depends(get_db)):
    db_uloga = db.query(Uloga).filter(Uloga.u_id == u_id).first()

    if db_uloga is None:
        raise HTTPException(status_code=404, detail="Uloga nije pronađena!")

    # Ažuriranje podataka uloge
    db_uloga.tip_uloge = novi_tip_uloge
    db.commit()

    return {"message": "Izmjena tipa uloge je uspjela!"} 



#HTTP GET dohvat filma sa sa petog servera  

@app.get("/uloga_za_film/", response_model=List[FilmPydantic], status_code=status.HTTP_200_OK)
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



# HTTP GET Dohvat glumaca sa prvog servera 

@app.get("/uloga_za_glumce/", response_model=List[GlumacPydantic], status_code=status.HTTP_200_OK)
async def dohvat_glumaca():
    glumci_url = "http://127.0.0.1:8000/glumci/"  
    try:
        with httpx.Client() as client:
            response = client.get(glumci_url)
            response.raise_for_status()  
        glumci = response.json()
        return glumci
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju glumca sa prvog servera: {e}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)