from fastapi import FastAPI, Depends, status, HTTPException   
from datetime import date
from pydantic import BaseModel 
from typing import List
import models  
from database import engine, SessionLocal  
from sqlalchemy.orm import Session  
import httpx    

from redatelji import RedateljPydantic  
from scenaristi import ScenaristPydantic  
from uloge import UlogaPydantic  
  

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

@app.post("/api/glumci/", status_code=status.HTTP_201_CREATED)  
async def stvori_glumca(glumac: GlumacCreate, db: Session = Depends(get_db)): 
    db_glumac = models.Glumac(**glumac.dict())
    db.add(db_glumac)
    db.commit()
    db.refresh(db_glumac)

    return {"msg": "Glumac je evidentiran!"}    

#HTTP GET dohvacanje svih glumaca    

@app.get("/api/glumci/", response_model=List[GlumacBase], status_code=status.HTTP_200_OK)
async def dohvati_sve_glumce(db: Session = db_dependency):
    glumci = db.query(models.Glumac).all()
    return glumci

#HTTP GET Dohvacanje jednog glumca  

@app.get("/api/glumac/{g_id}", status_code=status.HTTP_200_OK)
async def dohvati_glumca(g_id: str, db: Session = db_dependency):  
    glumac = db.query(models.Glumac).filter(models.Glumac.g_id == g_id).first()  
    if glumac is None:
        raise HTTPException(status_code=404, detail="Glumac nije pronadjen!")
    return glumac    

#HTTP PUT Izmjena osvojene nagrade za trecu glumicu   

@app.put("/api/glumac/{g_id}", status_code=status.HTTP_200_OK)
async def izmjena_nagrede_glumcu(g_id: str,nova_nagrada: str,db: Session = db_dependency):
    db_glumac = db.query(models.Glumac).filter(models.Glumac.g_id == g_id).first()

    if db_glumac is None:
        raise HTTPException(status_code=404, detail="Glumac nije pronadjen!")

    # Ažuriranje podataka posta
    db_glumac.g_nagrade = nova_nagrada
    db.commit()

    return {"message": "Izmjena nagrade glumcu je uspjela!"}    


#HTTP DELETE metoda brisanja glumca kojem nije dodijeljena niti jedna uloga 

@app.delete("/api/glumac/{g_id}", status_code=status.HTTP_204_NO_CONTENT)
async def obrisi_glumca(g_id: str, db: Session = db_dependency):
    db_glumac = db.query(models.Glumac).filter(models.Glumac.g_id == g_id).first()
    if db_glumac is None:
        raise HTTPException(status_code=404, detail="Glumac nije pronadjen!")
    db.delete(db_glumac)
    db.commit()

    return {"message": "Brisanje glumca je uspješno!"} 

 

#  HTTP dohvat redatelja sa drugog servera  

@app.get("/api/glumci_ka_redateljima/", response_model=List[RedateljPydantic], status_code=status.HTTP_200_OK)
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
  

# HTTP GET Dohvat scenarista sa treceg servera  

@app.get("/api/glumci_ka_scenaristima/", response_model=List[ScenaristPydantic], status_code=status.HTTP_200_OK)
async def dohvat_scenarista():
    scenaristi_url = "http://127.0.0.1:8002/api/scenaristi/"  
    try:
        with httpx.Client() as client:
            response =  client.get(scenaristi_url)
            response.raise_for_status() 
        scenaristi = response.json()
        return scenaristi
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju scenarista sa trećeg servera: {e}")
    

# HTTP Dohvat filmske uloge sa sestog servera  
    
@app.get("/api/filmske_uloge/", response_model=List[UlogaPydantic], status_code=status.HTTP_200_OK)
async def dohvat_filmskih_uloga():
    uloge_url = "http://127.0.0.1:8005/api/uloge/"  
    try:
        with httpx.Client() as client:
            response = client.get(uloge_url)
            response.raise_for_status()  
        uloge = response.json()
        return uloge
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju filmskih uloga sa šestog servera: {e}") 


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)