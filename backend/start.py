"""
Script to initialize the database and start the FastAPI application.

This script:
1. Waits for the MySQL database to be available
2. Creates the tables if they don't exist
3. Starts the FastAPI application
"""

import time
import sqlalchemy
import uvicorn
from db.database import engine
from db.models.base import Base
from db.models.SwiftCode import SwiftCode


def init_db():
    """Initialize the database by creating all tables."""
    retries = 5
    while retries > 0:
        try:
            print("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully.")
            return True
        except sqlalchemy.exc.OperationalError as e:
            if retries > 1:
                print(
                    f"Database connection failed. Retrying... ({retries-1} attempts left)")
                retries -= 1
                time.sleep(2)
            else:
                print(f"Error creating tables: {e}")
                return False


if __name__ == "__main__":
    if init_db():
        uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("Failed to initialize database. Exiting.")
