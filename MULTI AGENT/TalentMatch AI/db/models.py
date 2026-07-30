from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class RequisitionCache(Base):
    __tablename__ = "requisition_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_hash = Column(String, index=True, nullable=False)
    job_title = Column(String, nullable=False)
    results_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

class SalaryHistory(Base):
    __tablename__ = "salary_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String, index=True, nullable=False)
    candidate_name = Column(String, nullable=False)
    source = Column(String, nullable=False)
    expected_salary = Column(Float, nullable=True)
    currency = Column(String, default="EGP", nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class HiringSearchHistory(Base):
    __tablename__ = "hiring_search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String, nullable=False)
    filters_json = Column(Text, nullable=True)
    top_candidate_name = Column(String, nullable=True)
    top_candidate_salary = Column(Float, nullable=True)
    searched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
