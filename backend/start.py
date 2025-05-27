"""
Script to initialize the database and start the FastAPI application.

This script:
1. Waits for the MongoDB database to be available
2. Creates the indexes and collections if they don't exist
3. Inserts sample data if the collection is empty
4. Starts the FastAPI application
"""

import time
import uvicorn
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from db.database import get_database
from db.models.SwiftCode import SwiftCodeRepository


def init_db():
    """Initialize the database by creating indexes and inserting sample data."""
    retries = 10
    while retries > 0:
        try:
            print("Connecting to MongoDB...")
            db = get_database()

            # Test the connection
            db.command('ping')
            print("Connected to MongoDB successfully.")

            # Initialize SwiftCode repository
            swift_repo = SwiftCodeRepository(db)

            # Create unique index on swiftCode
            print("Creating database indexes...")
            swift_repo.create_index_sync()
            print("Database indexes created successfully.")

            # Insert sample data if collection is empty
            print("Checking for existing data...")
            sample_count = swift_repo.insert_sample_data()
            if sample_count > 0:
                print(f"Inserted {sample_count} sample SWIFT codes.")
            else:
                print("Database already contains data. Skipping sample data insertion.")

            print("Database initialization completed successfully.")
            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            if retries > 1:
                print(
                    f"Database connection failed. Retrying... ({retries-1} attempts left)")
                print(f"Error: {e}")
                retries -= 1
                time.sleep(3)
            else:
                print(f"Error connecting to database: {e}")
                return False
        except Exception as e:
            print(f"Unexpected error during database initialization: {e}")
            return False


if __name__ == "__main__":
    if init_db():
        print("Starting FastAPI application...")
        uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("Failed to initialize database. Exiting.")
        exit(1)
