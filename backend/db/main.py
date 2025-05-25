from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models.base import Base
from db.models.SwiftCode import SwiftCode

DB_USER = 'user'
DB_PASSWORD = 'userpassword'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'mydb'

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)


def initialize_database():
    """
    Create all tables defined by the models if they don't exist,
    and populate with sample data if tables are empty.
    """
    try:
        Base.metadata.create_all(engine)
        print("Database tables created successfully!")

        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            swift_code_count = session.query(SwiftCode).count()

            if swift_code_count == 0:
                print("Adding sample data to tables...")

                sample_swift_codes = [
                    SwiftCode(
                        swiftCode="DEUTDEFF",
                        address="Taunusanlage 12, 60325 Frankfurt am Main",
                        countryISO2="DE",
                        countryName="Germany",
                        isHeadquarter=False
                    ),
                    SwiftCode(
                        swiftCode="DEUTDEFFXXX",
                        address="Taunusanlage 12, 60325 Frankfurt am Main",
                        countryISO2="DE",
                        countryName="Germany",
                        isHeadquarter=True
                    ),
                    SwiftCode(
                        swiftCode="CHASUS33",
                        address="270 Park Avenue, New York",
                        countryISO2="US",
                        countryName="United States",
                        isHeadquarter=False
                    ),
                    SwiftCode(
                        swiftCode="CHASJPJT",
                        address="Tokyo Building, 2-7-3, Marunouchi, Chiyoda-ku",
                        countryISO2="JP",
                        countryName="Japan",
                        isHeadquarter=False
                    )
                ]

                for swift_code in sample_swift_codes:
                    session.add(swift_code)

                session.commit()
                print(
                    f"Added {len(sample_swift_codes)} sample SWIFT codes to the database")
            else:
                print(
                    f"Database already contains data ({swift_code_count} SWIFT codes found). Skipping sample data insertion.")

        except Exception as data_error:
            session.rollback()
            print(f"Error adding sample data: {data_error}")
            raise

        finally:
            session.close()

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    initialize_database()
