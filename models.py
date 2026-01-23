from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Read-only / Form Input fields
    nama_tersangka = db.Column(db.String(200))
    umur_tersangka = db.Column(db.Integer) # New Field
    kategori_umur = db.Column(db.String(20), default='Dewasa') # Dewasa or Anak
    pasal = db.Column(db.String(200))
    jpu = db.Column(db.String(200)) # New Field
    spdp = db.Column(db.String(200), nullable=True) # Legacy field
    
    # New SPDP Fields
    spdp_tgl_terima = db.Column(db.String(50)) # Kejaksaan Received Date
    spdp_ket_terima = db.Column(db.String(200)) # Kejaksaan Details
    spdp_tgl_polisi = db.Column(db.String(50)) # Police Date
    spdp_ket_polisi = db.Column(db.String(200)) # Police Details
    
    # Editable Stage fields
    berkas_tahap_1 = db.Column(db.String(200)) # e.g. "01-01-2023"
    p18_p19 = db.Column(db.String(200))
    p21 = db.Column(db.String(200))
    tahap_2 = db.Column(db.String(200))
    limpah_pn = db.Column(db.String(200))
    keterangan = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.now)

    @property
    def is_complete(self):
        """Check if SPDP, Tahap 1, P18/19, P21, and Tahap 2 are all filled"""
        return all([
            self.spdp_tgl_terima,
            self.berkas_tahap_1, 
            self.p18_p19, 
            self.p21, 
            self.tahap_2
        ])

    def to_dict(self):
        return {
            'id': self.id,
            'nama_tersangka': self.nama_tersangka,
            'umur_tersangka': self.umur_tersangka,
            'kategori_umur': self.kategori_umur,
            'pasal': self.pasal,
            'jpu': self.jpu,
            'spdp': self.spdp,
            'berkas_tahap_1': self.berkas_tahap_1,
            'p18_p19': self.p18_p19,
            'p21': self.p21,
            'tahap_2': self.tahap_2,
            'limpah_pn': self.limpah_pn,
            'keterangan': self.keterangan
        }
