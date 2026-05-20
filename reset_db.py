from sqlalchemy import text
from app.database import engine

def reset_database():
    with engine.connect() as conn:
        print("⚠️ DROPPING ALL TABLES (CASCADE)...")

        conn.execute(text("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
        """))

        conn.commit()
        print("✅ ALL tables dropped completely.")

if __name__ == "__main__":
    reset_database()
