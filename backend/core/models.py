from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Example model
# from sqlalchemy import Column, Integer, String
# class Mission(Base):
#     __tablename__ = "missions"
#     id = Column(Integer, primary_key=True, index=True)
#     prompt = Column(String, index=True) 