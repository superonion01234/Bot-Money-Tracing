from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime
from database import Base
from datetime import datetime

class Transaksi(Base):
    __tablename__ = "transaksi"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    jenis = Column(String)  # Pengeluaran / Pemasukan / Menabung
    kategori = Column(String)
    jumlah = Column(Numeric)
    tanggal = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    note = Column(String, default="")

class TargetMenabung(Base):
    __tablename__ = "target_menabung"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    kategori = Column(String, index=True)
    target = Column(Numeric)

class TransaksiEmas(Base):
    __tablename__ = "transaksi_emas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    berat_gram = Column(Numeric)   # berat dalam gram
    tanggal = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    note = Column(String, default="")