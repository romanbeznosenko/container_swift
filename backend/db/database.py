"""
Database connection module for MongoDB.

This module provides the MongoDB connection and database instance for the application.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from typing import Optional

# Database configuration
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "mongodb://root:rootpassword@mongodb:27017/mydb?authSource=admin"
)
DATABASE_NAME = "mydb"

# Global variables for database connections
mongo_client: Optional[MongoClient] = None
async_mongo_client: Optional[AsyncIOMotorClient] = None
database = None
async_database = None


def get_database():
    """
    Get the synchronous MongoDB database instance.

    Returns:
        pymongo.database.Database: The MongoDB database instance
    """
    global mongo_client, database

    if mongo_client is None:
        mongo_client = MongoClient(DATABASE_URL)
        database = mongo_client[DATABASE_NAME]

    return database


async def get_async_database():
    """
    Get the asynchronous MongoDB database instance.

    Returns:
        motor.motor_asyncio.AsyncIOMotorDatabase: The async MongoDB database instance
    """
    global async_mongo_client, async_database

    if async_mongo_client is None:
        async_mongo_client = AsyncIOMotorClient(DATABASE_URL)
        async_database = async_mongo_client[DATABASE_NAME]

    return async_database


def close_database_connections():
    """Close all database connections."""
    global mongo_client, async_mongo_client

    if mongo_client:
        mongo_client.close()
        mongo_client = None

    if async_mongo_client:
        async_mongo_client.close()
        async_mongo_client = None


# Dependency for FastAPI
def get_db():
    """
    Dependency for getting a database instance in FastAPI routes.

    Yields:
        pymongo.database.Database: The MongoDB database instance
    """
    try:
        db = get_database()
        yield db
    finally:
        # MongoDB connections are managed at the client level
        pass
