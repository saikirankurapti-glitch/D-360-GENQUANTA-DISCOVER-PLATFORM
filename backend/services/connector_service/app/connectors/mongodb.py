import json
from datetime import datetime, date
from typing import Dict, Any, List, Tuple
from pymongo import MongoClient
from app.connectors.base import BaseConnector

class MongoDBConnector(BaseConnector):
    """
    MongoDB database connector.
    Supports dynamic schema discovery by sampling documents, connection testing,
    and structured query execution (translating filters to MongoDB filter documents).
    """

    def __init__(self, credentials: Dict[str, Any], additional_params: Dict[str, Any] = None):
        super().__init__(credentials, additional_params)
        self.client = None
        self.db = None

    async def connect(self) -> None:
        if not self.client:
            connection_uri = self.credentials.get("connection_uri")
            database_name = self.credentials.get("database")

            # Fallbacks if connection_uri not directly provided
            if not connection_uri:
                host = self.credentials.get("host", "localhost")
                port = self.credentials.get("port", 27017)
                username = self.credentials.get("username")
                password = self.credentials.get("password")
                
                if username and password:
                    connection_uri = f"mongodb://{username}:{password}@{host}:{port}/{database_name or ''}"
                else:
                    connection_uri = f"mongodb://{host}:{port}/{database_name or ''}"

            if not database_name:
                raise ValueError("Database name is required for MongoDB connector configuration.")

            # Create MongoClient with a short timeout to fail fast
            self.client = MongoClient(connection_uri, serverSelectionTimeoutMS=3000)
            self.db = self.client[database_name]

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    async def test_connection(self) -> Tuple[bool, str]:
        try:
            await self.connect()
            # The ping command is cheap and triggers server selection
            self.client.admin.command('ping')
            return True, "Successfully connected to MongoDB server."
        except Exception as e:
            return False, f"MongoDB connection test failed: {str(e)}"

    async def discover_schema(self) -> List[Dict[str, Any]]:
        await self.connect()
        entities = []

        # Get list of collection names
        collections = self.db.list_collection_names()
        for col_name in collections:
            # Skip system collections
            if col_name.startswith("system."):
                continue

            # Sample up to 10 documents to discover keys and type profile
            sample_docs = list(self.db[col_name].find().limit(10))
            discovered_fields = {}

            # Map fields and infer their data types
            for doc in sample_docs:
                for key, val in doc.items():
                    if key not in discovered_fields:
                        data_type = "string"
                        if isinstance(val, bool):
                            data_type = "boolean"
                        elif isinstance(val, int):
                            data_type = "integer"
                        elif isinstance(val, float):
                            data_type = "float"
                        elif isinstance(val, (datetime, date)):
                            data_type = "date"
                        
                        discovered_fields[key] = {
                            "physical_name": key,
                            "display_name": key.replace("_", " ").title(),
                            "data_type": data_type,
                            "is_nullable": True,
                            "is_primary_key": key == "_id",
                            "description": f"Field '{key}' discovered from MongoDB collection '{col_name}'"
                        }

            # If the collection is empty, default to at least having '_id'
            if "_id" not in discovered_fields:
                discovered_fields["_id"] = {
                    "physical_name": "_id",
                    "display_name": "ID",
                    "data_type": "string",
                    "is_nullable": False,
                    "is_primary_key": True,
                    "description": "Primary document identifier"
                }

            entities.append({
                "physical_name": col_name,
                "display_name": col_name.replace("_", " ").title(),
                "description": f"MongoDB collection '{col_name}'",
                "fields": list(discovered_fields.values())
            })

        return entities

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        await self.connect()
        entity = query["entity"]
        fields = query["fields"]
        filters = query.get("filters") or []
        limit = query.get("limit", 100)

        # Build MongoDB filter doc
        mongo_filters = {}
        for f in filters:
            field = f["field"]
            op = f["operator"]
            val = f["value"]

            if op == "=":
                mongo_filters[field] = val
            elif op == "!=":
                mongo_filters[field] = {"$ne": val}
            elif op == ">":
                mongo_filters[field] = {"$gt": val}
            elif op == ">=":
                mongo_filters[field] = {"$gte": val}
            elif op == "<":
                mongo_filters[field] = {"$lt": val}
            elif op == "<=":
                mongo_filters[field] = {"$lte": val}
            elif op.upper() == "LIKE":
                mongo_filters[field] = {"$regex": str(val), "$options": "i"}
            elif op.upper() == "IN":
                mongo_filters[field] = {"$in": val if isinstance(val, list) else [val]}

        # Build projection
        projection = {f: 1 for f in fields}
        # Ensure _id is not implicitly added if not requested
        if "_id" not in fields:
            projection["_id"] = 0

        cursor = self.db[entity].find(mongo_filters, projection).limit(limit)

        rows = []
        for doc in cursor:
            row_data = []
            for f in fields:
                val = doc.get(f)
                if val is None:
                    row_data.append(None)
                elif isinstance(val, (dict, list)):
                    row_data.append(json.dumps(val))
                elif hasattr(val, "__str__") and not isinstance(val, (str, int, float, bool)):
                    row_data.append(str(val))
                else:
                    row_data.append(val)
            rows.append(row_data)

        return fields, rows

    async def preview_data(self, entity_name: str, limit: int = 10) -> Tuple[List[str], List[List[Any]]]:
        await self.connect()
        # Find fields from discover_schema
        schema = await self.discover_schema()
        fields = []
        for ent in schema:
            if ent["physical_name"] == entity_name:
                fields = [f["physical_name"] for f in ent["fields"]]
                break
        if not fields:
            fields = ["_id"]

        projection = {f: 1 for f in fields}
        cursor = self.db[entity_name].find({}, projection).limit(limit)

        rows = []
        for doc in cursor:
            row_data = []
            for f in fields:
                val = doc.get(f)
                if val is None:
                    row_data.append(None)
                elif isinstance(val, (dict, list)):
                    row_data.append(json.dumps(val))
                elif hasattr(val, "__str__") and not isinstance(val, (str, int, float, bool)):
                    row_data.append(str(val))
                else:
                    row_data.append(val)
            rows.append(row_data)

        return fields, rows

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "mongodb",
            "name": "MongoDB Database",
            "description": "Connects to MongoDB document databases",
            "required_credentials": ["host", "port", "database", "username", "password"],
            "supported_operations": ["filter", "limit"]
        }
