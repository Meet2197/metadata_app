from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.db import Base
import uuid
import datetime

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    acquisition_date = Column(DateTime, default=datetime.datetime.utcnow)
    microscope = Column(String)
    objective = Column(String)
    pixel_size_xy = Column(Float)
    channels = Column(ARRAY(String))
    raw_path = Column(String)
    eln_id = Column(String)
