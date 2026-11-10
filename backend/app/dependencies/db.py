from sqlalchemy.orm import Session
from backend.app.database import engine



def get_session():

    with Session(engine) as session:
        yield session