from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base    

class Glumac(Base):
    __tablename__ = "glumci"

    g_id = Column(String(10), primary_key=True, index=True)
    g_ime = Column(String(50), index=True)
    g_prezime = Column(String(50), index=True)
    g_datum_rodjenja = Column(Date)
    g_mjesto_rodjenja = Column(String)
    g_nacionalnost = Column(String)
    g_nagrade = Column(String(100))

    uloge = relationship("Uloga", back_populates="glumac")

class Redatelj(Base):
    __tablename__="redatelji"

    r_id=Column(String(10), primary_key=True, unique=True)
    r_ime=Column(String(50))
    r_prezime=Column(String(50))
    r_datum_rodjenja=Column(Date)
    r_email=Column(String(50), unique=True)
    r_telefon=Column(Integer, unique=True)
    r_karijera_pocetak=Column(Date)
    r_karijera_kraj=Column(Date)
    r_nagrade=Column(String(100))  
    
    filmovi = relationship('Film', back_populates='redatelj')   

class Scenarist(Base):
    __tablename__="scenaristi"   

    s_id=Column(String(10), primary_key=True, unique=True)
    s_ime=Column(String(50))
    s_prezime=Column(String(50))
    s_datum_rodjenja=Column(Date)
    s_email=Column(String(50), unique=True)
    s_telefon=Column(Integer, unique=True)
    s_karijera_pocetak=Column(Date)
    s_karijera_kraj=Column(Date)
    s_nagrade=Column(String(100))    

    filmovi = relationship('Film', back_populates='scenarist')   

class Film(Base):  
    __tablename__="filmovi"    

    f_id=Column(Integer, primary_key=True, index=True)
    f_naslov=Column(String(50))
    f_godina=Column(Integer) 
    f_zanr=Column(String(50))   
    f_trajanje_u_minutama=Column(Integer)  

    r_id = Column(String(10), ForeignKey('redatelji.r_id'))
    s_id = Column(String(10), ForeignKey('scenaristi.s_id'))   
    st_id=Column(Integer, ForeignKey('studios.st_id'))   

    redatelj = relationship('Redatelj', back_populates='filmovi')
    scenarist = relationship('Scenarist', back_populates='filmovi')  
    studio=relationship('Studio', back_populates='filmovi')  
    ocjene_gledanosti = relationship('Ocjena', back_populates='film')   
    uloge=relationship("Uloga", back_populates="film")

class Studio(Base):
    __tablename__="studios"

    st_id=Column(Integer, primary_key=True, index=True)  
    st_naziv=Column(String(50))
    st_godina_osnutka=Column(Integer)  

    filmovi = relationship('Film', back_populates='studio')  

class Ocjena(Base):

    __tablename__="ocjene_gledanosti" 

    m_id=Column(Integer, primary_key=True, index=True) 
    f_id=Column(Integer, ForeignKey('filmovi.f_id'))   
    ocjena=Column(Float)  
    komentar=Column(String(200))  
    datum_ocjenjivanja=Column(Date)  

    film = relationship('Film', back_populates='ocjene_gledanosti') 

class Uloga(Base):
    __tablename__ = "uloge"

    u_id = Column(Integer, primary_key=True, index=True)
    f_id = Column(Integer, ForeignKey('filmovi.f_id'))
    g_id = Column(String(10), ForeignKey('glumci.g_id'))
    uloga = Column(String(255))
    tip_uloge = Column(String(30))

    glumac = relationship("Glumac", back_populates="uloge")  

    film=relationship("Film", back_populates="uloge")



