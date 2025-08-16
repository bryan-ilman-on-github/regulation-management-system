from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from uuid import UUID
import datetime

# Shared properties
class RegulationBase(BaseModel):
    nama_peraturan: Optional[str] = None
    link_peraturan: Optional[str] = None
    tipe_dokumen: Optional[str] = None
    judul: Optional[str] = None
    tahun: Optional[str] = None
    status: Optional[str] = None

# Properties to receive on item creation
class RegulationCreate(RegulationBase):
    # Make fields required for creation
    nama_peraturan: str
    judul: str
    tahun: str

# Properties to receive on item update
class RegulationUpdate(RegulationBase):
    pass

# Properties shared by models stored in DB
class RegulationInDBBase(RegulationBase):
    regulation_id: UUID
    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Regulation(RegulationInDBBase):
    # This is the full model returned by the API
    materi_pokok: Optional[str] = None
    teu: Optional[str] = None
    nomor: Optional[str] = None
    bentuk: Optional[str] = None
    bentuk_singkat: Optional[str] = None
    tempat_penetapan: Optional[str] = None
    tanggal_penetapan: Optional[datetime.date] = None
    tanggal_pengundangan: Optional[datetime.date] = None
    tanggal_berlaku: Optional[datetime.date] = None
    sumber: Optional[str] = None
    bahasa: Optional[str] = None
    lokasi: Optional[str] = None
    bidang: Optional[str] = None
    subjek: Optional[str] = None
    dicabut_dengan: Optional[Any] = None
    mencabut: Optional[Any] = None
    diubah_dengan: Optional[Any] = None
    mengubah: Optional[Any] = None
    ujimateri_mk: Optional[Any] = None
    file_peraturan: Optional[Any] = None
    file_pdf: Optional[str] = None