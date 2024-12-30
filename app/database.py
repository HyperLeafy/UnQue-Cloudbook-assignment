from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# path for database (SQLite3)
DATABASE_path = "sqlite:///./college_apppointment.db"

# creating database engine
db_engine = create_engine(DATABASE_path)

# initalizing a base class for database
base = declarative_base()

# starting local sessions this is to imported in other script to grant access to session
session_local = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


# creating User database model/tabel
class User(base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    designation = Column(String,nullable=False)
    

class Availability(base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_slot = Column(String, nullable=False)

    professor = relationship("User", back_populates="availabilities")
    

# creating appointment database model/tabel
class Appointment(base):
    __tablename__ = "appointment"
    
    id = Column(Integer, primary_key=True, index=True)
    # set/defines the foreign key to be assossiated   
    professor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_slot = Column(String, nullable=False)
    
    professor = relationship("User", foreign_keys=[professor_id])
    student = relationship("User", foreign_keys=[student_id])


User.availabilities = relationship("Availability", back_populates="professor")

def db_init():
    base.metadata.drop_all(bind=db_engine)
    base.metadata.create_all(bind=db_engine)