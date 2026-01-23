import pandas as pd
from app import app, db
from models import Case

def import_excel():
    excel_file = 'FORMAT.xlsx'
    try:
        df = pd.read_excel(excel_file)
        
        # Check if DB is empty
        if Case.query.first():
            print("Database already contains data. Skipping import.")
            return

        print("Importing data from Excel...")
        for _, row in df.iterrows():
            # Handle NaN values
            def clean(val):
                if pd.isna(val):
                    return ""
                return str(val).strip()

            new_case = Case(
                nama_tersangka=clean(row.get('NAMA TERSANGKA')),
                pasal=clean(row.get('PASAL YANG DISANGKAKAN')),
                spdp=clean(row.get('SPDP')),
                berkas_tahap_1=clean(row.get('BERKAS TAHAP I')),
                p18_p19=clean(row.get('P-18 / P-19')),
                p21=clean(row.get('P-21')),
                tahap_2=clean(row.get('TAHAP II')),
                limpah_pn=clean(row.get('LIMPAH PN')),
                keterangan=clean(row.get('KETERANGAN'))
            )
            db.session.add(new_case)
        
        db.session.commit()
        print("Import successful!")
        
    except FileNotFoundError:
        print(f"File {excel_file} not found.")
    except Exception as e:
        print(f"Error during import: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin here too just in case
        from app import create_admin
        create_admin()
        import_excel()
