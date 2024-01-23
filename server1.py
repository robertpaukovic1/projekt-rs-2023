from fastapi import FastAPI, Depends, status, HTTPException   
from datetime import date
from pydantic import BaseModel 
from typing import List
import models  
from database import engine, SessionLocal  
from sqlalchemy.orm import Session  
import httpx    

from server2 import RedateljPydantic  
from server3 import ScenaristPydantic  
from server6 import UlogaPydantic  
  

app=FastAPI()  

models.Base.metadata.create_all(bind=engine)   

#Pydantic model za glumce  

class GlumacPydantic(BaseModel):
   g_id: str  
   g_ime: str  
   g_prezime: str 
   g_datum_rodjenja: date   
   g_mjesto_rodjenja: str  
   g_nacionalnost: str  
   g_nagrade:str  

#Base model za glumce 

class GlumacBase(BaseModel):
   g_id: str  
   g_ime: str  
   g_prezime: str 
   g_datum_rodjenja: date   
   g_mjesto_rodjenja: str  
   g_nacionalnost: str  
   g_nagrade:str  

class GlumacCreate(GlumacBase):
    pass   


#Dohvacanje sheme baze

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()  

db_dependency = Depends(get_db)   

#HTTP Uvodna GET metoda   

@app.get("/")
def root():
    return {"msg": "Ovo radi!"}     

#HTTP POST Unos podataka o glumcima  

@app.post("/glumci/", status_code=status.HTTP_201_CREATED)  
async def stvori_glumca(glumac: GlumacCreate, db: Session = Depends(get_db)): 
    db_glumac = models.Glumac(**glumac.dict())
    db.add(db_glumac)
    db.commit()
    db.refresh(db_glumac)

    return {"msg": "Glumac je evidentiran!"}    

#HTTP GET dohvacanje svih glumaca    

@app.get("/glumci/", response_model=List[GlumacBase], status_code=status.HTTP_200_OK)
async def dohvati_sve_glumce(db: Session = db_dependency):
    glumci = db.query(models.Glumac).all()
    return glumci

#HTTP GET Dohvacanje jednog glumca  

@app.get("/glumac/{g_id}", status_code=status.HTTP_200_OK)
async def dohvati_glumca(g_id: str, db: Session = db_dependency):  
    glumac = db.query(models.Glumac).filter(models.Glumac.g_id == g_id).first()  
    if glumac is None:
        raise HTTPException(status_code=404, detail="Glumac nije pronadjen!")
    return glumac    

#HTTP PUT Izmjena osvojene nagrade za trecu glumicu   

@app.put("/glumac/{g_id}", status_code=status.HTTP_200_OK)
async def izmjena_nagrede_glumcu(g_id: str,nova_nagrada: str,db: Session = db_dependency):
    db_glumac = db.query(models.Glumac).filter(models.Glumac.g_id == g_id).first()

    if db_glumac is None:
        raise HTTPException(status_code=404, detail="Glumac nije pronadjen!")

    # Ažuriranje podataka posta
    db_glumac.g_nagrade = nova_nagrada
    db.commit()

    return {"message": "Izmjena nagrade glumcu je uspjela!"}    


#HTTP DELETE metoda brisanja glumca kojem nije dodijeljena niti jedna uloga 

@app.delete("/glumac/{g_id}", status_code=status.HTTP_204_NO_CONTENT)
async def obrisi_glumca(g_id: str, db: Session = db_dependency):
    db_glumac = db.query(models.Glumac).filter(models.Glumac.g_id == g_id).first()

    if db_glumac is None:
        raise HTTPException(status_code=404, detail="Glumac nije pronadjen!")

    # Brisanje glumca sa tablice glumaca 
    db.delete(db_glumac)
    db.commit()

    return {"message": "Brisanje glumca je uspješno!"} 

 

#  HTTP dohvat redatelja sa drugog servera  

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
  

# HTTP GET Dohvat scenarista sa treceg servera  

@app.get("/dohvati-scenariste-sa-treceg-servera/", response_model=List[ScenaristPydantic], status_code=status.HTTP_200_OK)
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
    

# HTTP Dohvat filmske uloge sa sestog servera  
    
@app.get("/dohvat-filmskih-uloga-sa-sestog-servera/", response_model=List[UlogaPydantic], status_code=status.HTTP_200_OK)
async def dohvati_filmske_uloge_sa_sestog_servera():
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)