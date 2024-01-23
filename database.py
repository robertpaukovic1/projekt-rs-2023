from sqlalchemy import create_engine  
from sqlalchemy.orm import sessionmaker  
from sqlalchemy.ext.declarative import declarative_base  

URL_DATABASE = 'mysql+pymysql://root:#gLista11G8@localhost:3306/Filmoteka'

engine = create_engine(URL_DATABASE) 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)     

Base = declarative_base()
