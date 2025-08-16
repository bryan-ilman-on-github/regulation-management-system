from ..core.database import Base
from sqlalchemy import Column, String, Text, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Regulation(Base):
    __tablename__ = "regulation"

    regulation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_peraturan = Column(Text)
    link_peraturan = Column(Text)
    tipe_dokumen = Column(String(100))
    materi_pokok = Column(Text)
    judul = Column(Text)
    teu = Column(Text)
    nomor = Column(String(100))
    bentuk = Column(String(100))
    bentuk_singkat = Column(String(50))
    tahun = Column(String(4))
    tempat_penetapan = Column(String(255))
    tanggal_penetapan = Column(Date)
    tanggal_pengundangan = Column(Date)
    tanggal_berlaku = Column(Date)
    sumber = Column(String(255))
    status = Column(String(50))
    bahasa = Column(String(50))
    lokasi = Column(String(255))
    bidang = Column(String(255))
    subjek = Column(String(255))
    dicabut_dengan = Column(JSON)
    mencabut = Column(JSON)
    diubah_dengan = Column(JSON)
    mengubah = Column(JSON)
    ujimateri_mk = Column(JSON)
    file_peraturan = Column(JSON)
    file_pdf = Column(String(500))
