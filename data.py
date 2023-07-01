import sqlalchemy as sq
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy_utils import database_exists, create_database, drop_database
from config import db_url_object

metadata = MetaData()
Base = declarative_base()
engine = create_engine(db_url_object)

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

def check_and_create_database(db_url_object):
    if not database_exists(db_url_object):
        create_database(db_url_object)

def add_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id = profile_id, worksheet_id = worksheet_id)
        session.add(to_bd)
        session.commit()

def check_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(
            Viewed.profile_id == profile_id,
            Viewed.worksheet_id == worksheet_id
            ).first()
        return True if from_bd else False

# if __name__ == "__main__":
#     engine = create_engine(db_url_object)
#     Base.metadata.create_all(engine)
#     add_user(engine, 2113, 123456)
#     res = check_user(engine, 2113, 123456)
#     print(res)