"""
Script untuk menambahkan kolom kategori_umur ke tabel Case
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Case

def add_kategori_umur_column():
    """Add kategori_umur column to Case table"""
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('case')]
            
            if 'kategori_umur' in columns:
                print("✓ Column 'kategori_umur' already exists")
                return
            
            # Add column using raw SQL
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    'ALTER TABLE "case" ADD COLUMN kategori_umur VARCHAR(20) DEFAULT \'Dewasa\''
                ))
                conn.commit()
            
            print("✓ Successfully added 'kategori_umur' column")
            
            # Update existing records to have default value
            cases = Case.query.all()
            for case in cases:
                if not case.kategori_umur:
                    case.kategori_umur = 'Dewasa'
            db.session.commit()
            
            print(f"✓ Updated {len(cases)} existing records with default value 'Dewasa'")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_kategori_umur_column()
