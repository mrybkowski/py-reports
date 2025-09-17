"""MongoDB client wrapper with connection management."""

import logging
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB client wrapper with connection management and error handling."""
    
    def __init__(self, connection_url: str = None, database_name: str = None):
        self.settings = get_settings()
        self.connection_url = connection_url or self.settings.mongodb_url
        self.database_name = database_name or self.settings.mongodb_database
        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None
        self._connected = False
    
    def connect(self) -> bool:
        """Establish connection to MongoDB."""
        try:
            # Build connection options
            connection_options = {
                'serverSelectionTimeoutMS': 5000,
                'connectTimeoutMS': 5000,
                'socketTimeoutMS': 5000,
            }
            
            # Add authentication if provided
            if self.settings.mongodb_username and self.settings.mongodb_password:
                connection_options['username'] = self.settings.mongodb_username
                connection_options['password'] = self.settings.mongodb_password
            
            # Add TLS if URL contains ssl=true
            if 'ssl=true' in self.connection_url.lower():
                connection_options['tls'] = True
                connection_options['tlsAllowInvalidCertificates'] = False
            
            self._client = MongoClient(self.connection_url, **connection_options)
            
            # Test connection
            self._client.admin.command('ping')
            self._database = self._client[self.database_name]
            self._connected = True
            
            logger.info(f"Successfully connected to MongoDB: {self.database_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
    
    def is_connected(self) -> bool:
        """Check if client is connected to MongoDB."""
        if not self._connected or not self._client:
            return False
        
        try:
            # Test connection
            self._client.admin.command('ping')
            return True
        except Exception:
            self._connected = False
            return False
    
    def get_database(self) -> Database:
        """Get database instance."""
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")
        return self._database
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get collection instance."""
        database = self.get_database()
        return database[collection_name]
    
    def execute_aggregation(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute aggregation pipeline on a collection.
        
        Args:
            collection_name: Name of the collection
            pipeline: MongoDB aggregation pipeline
            
        Returns:
            List of documents from aggregation result
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")
        
        try:
            collection = self.get_collection(collection_name)
            logger.info(f"Executing aggregation on {collection_name} with {len(pipeline)} stages")
            
            # Log pipeline for debugging (first 3 stages only)
            for i, stage in enumerate(pipeline[:3]):
                logger.debug(f"Pipeline stage {i+1}: {stage}")
            
            cursor = collection.aggregate(pipeline)
            results = list(cursor)
            
            logger.info(f"Aggregation completed, returned {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute aggregation on {collection_name}: {e}")
            raise
    
    def execute_find(self, collection_name: str, query: Dict[str, Any] = None, 
                    projection: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """
        Execute find query on a collection.
        
        Args:
            collection_name: Name of the collection
            query: MongoDB find query
            projection: Fields to include/exclude
            limit: Maximum number of documents to return
            
        Returns:
            List of documents from find result
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")
        
        try:
            collection = self.get_collection(collection_name)
            logger.info(f"Executing find on {collection_name}")
            
            cursor = collection.find(query or {}, projection)
            
            if limit:
                cursor = cursor.limit(limit)
            
            results = list(cursor)
            
            logger.info(f"Find completed, returned {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute find on {collection_name}: {e}")
            raise
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics."""
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")
        
        try:
            collection = self.get_collection(collection_name)
            stats = collection.aggregate([{"$collStats": {"count": {}}}]).next()
            return stats
        except Exception as e:
            logger.error(f"Failed to get collection stats for {collection_name}: {e}")
            return {}
    
    def list_collections(self) -> List[str]:
        """List all collections in the database."""
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")
        
        try:
            database = self.get_database()
            return database.list_collection_names()
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []


# Global MongoDB client instance
_mongodb_client: Optional[MongoDBClient] = None


def get_mongodb_client(connection_url: str = None, database_name: str = None) -> MongoDBClient:
    """Get MongoDB client instance (singleton pattern)."""
    global _mongodb_client
    if _mongodb_client is None:
        _mongodb_client = MongoDBClient(connection_url, database_name)
    return _mongodb_client