from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///trainer.db"
engine = create_engine(DATABASE_URL, echo=True)

def get_db():
    with Session(engine) as session:
        yield session
