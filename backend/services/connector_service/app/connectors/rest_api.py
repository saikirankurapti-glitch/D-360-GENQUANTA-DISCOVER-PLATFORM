import httpx
import base64
from typing import Dict, Any, List, Tuple
from app.connectors.base import BaseConnector

class RestApiConnector(BaseConnector):
    """
    Production-grade Generic REST API connector.
    Communicates with HTTP/JSON endpoints, manages headers and authentication,
    infers JSON response schemas dynamically, and maps queries to HTTP request parameters.
    """
    
    def __init__(self, credentials: Dict[str, Any], additional_params: Dict[str, Any] = None):
        super().__init__(credentials, additional_params)
        self.base_url = None
        self.headers = {}
        self.client = None

    async def connect(self) -> None:
        if self.client:
            return
            
        self.base_url = self.credentials.get("base_url")
        if not self.base_url:
            raise ValueError("base_url is required for REST API connector.")
            
        auth_type = self.credentials.get("auth_type", "none").lower()
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "AnalytiX-Connector-Service/1.0"
        }
        
        # Configure auth headers
        if auth_type == "bearer":
            token = self.credentials.get("token")
            if not token:
                raise ValueError("token is required for Bearer authentication.")
            self.headers["Authorization"] = f"Bearer {token}"
            
        elif auth_type == "basic":
            username = self.credentials.get("username")
            password = self.credentials.get("password")
            if not username or not password:
                raise ValueError("username and password are required for Basic authentication.")
            auth_str = f"{username}:{password}"
            auth_b64 = base64.b64encode(auth_str.encode()).decode()
            self.headers["Authorization"] = f"Basic {auth_b64}"
            
        elif auth_type == "custom_header":
            header_name = self.credentials.get("header_name")
            header_value = self.credentials.get("header_value")
            if header_name and header_value:
                self.headers[header_name] = header_value
                
        # Initialize httpx client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=10.0
        )

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None

    async def test_connection(self) -> Tuple[bool, str]:
        try:
            await self.connect()
            test_path = self.additional_params.get("test_path", "/")
            response = await self.client.get(test_path)
            if response.status_code >= 400:
                return False, f"REST API test connection failed with status code: {response.status_code}"
            return True, "Successfully reached the REST API endpoint."
        except Exception as e:
            return False, f"REST API connection failed: {str(e)}"
        finally:
            await self.disconnect()

    async def discover_schema(self) -> List[Dict[str, Any]]:
        await self.connect()
        endpoints = self.additional_params.get("endpoints")
        
        # Default fallback endpoint if not defined
        if not endpoints:
            endpoints = [{"path": "", "name": "Data"}]
            
        entities = []
        for ep in endpoints:
            path = ep["path"]
            name = ep.get("name", path.strip("/").replace("_", " ").title())
            
            try:
                # Attempt to query endpoint to dynamically reflect schema keys
                response = await self.client.get(path)
                fields = []
                if response.status_code == 200:
                    data = response.json()
                    sample_item = {}
                    
                    # Extract sample item from array or paginated envelope
                    if isinstance(data, list) and len(data) > 0:
                        sample_item = data[0]
                    elif isinstance(data, dict):
                        for key in ["results", "items", "data", "records"]:
                            if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                                sample_item = data[key][0]
                                break
                        if not sample_item:
                            sample_item = data
                            
                    # Parse properties
                    for k, v in sample_item.items():
                        data_type = "string"
                        if isinstance(v, bool):
                            data_type = "boolean"
                        elif isinstance(v, int):
                            data_type = "integer"
                        elif isinstance(v, float):
                            data_type = "float"
                        elif isinstance(v, (dict, list)):
                            data_type = "string"
                            
                        fields.append({
                            "physical_name": k,
                            "display_name": k.replace("_", " ").title(),
                            "data_type": data_type,
                            "is_nullable": True,
                            "is_primary_key": k.lower() in ["id", "uuid", "key", "pk"],
                            "description": f"Field '{k}' returned by API"
                        })
                
                # Default fields if discovery returned empty columns
                if not fields:
                    fields = [
                        {"physical_name": "id", "display_name": "ID", "data_type": "integer", "is_nullable": False, "is_primary_key": True},
                        {"physical_name": "name", "display_name": "Name", "data_type": "string", "is_nullable": True, "is_primary_key": False}
                    ]
                    
                entities.append({
                    "physical_name": path,
                    "display_name": name,
                    "description": f"REST API endpoint '{path}'",
                    "fields": fields
                })
            except Exception:
                # Add default entity on connection error
                entities.append({
                    "physical_name": path,
                    "display_name": name,
                    "description": f"REST API endpoint '{path}' (offline reflection)",
                    "fields": [
                        {"physical_name": "id", "display_name": "ID", "data_type": "integer", "is_nullable": False, "is_primary_key": True},
                        {"physical_name": "name", "display_name": "Name", "data_type": "string", "is_nullable": True, "is_primary_key": False}
                    ]
                })
                
        await self.disconnect()
        return entities

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        await self.connect()
        path = query["entity"]  # Endpoint path e.g. /compounds
        fields = query["fields"]
        filters = query.get("filters") or []
        limit = query.get("limit", 100)
        
        # Build HTTP Query Parameters
        params = {}
        for f in filters:
            field = f["field"]
            op = f["operator"]
            val = f["value"]
            if op == "=":
                params[field] = val
            elif op.upper() == "LIKE":
                params[f"{field}_contains"] = val
                
        limit_param = self.additional_params.get("limit_parameter_name", "limit")
        params[limit_param] = limit
        
        response = await self.client.get(path, params=params)
        if response.status_code != 200:
            raise ValueError(f"REST API query failed ({response.status_code}): {response.text}")
            
        data = response.json()
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ["results", "items", "data", "records"]:
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            if not items:
                items = [data]
                
        # Filter fields and yield rows
        rows = []
        for item in items:
            row = []
            for f in fields:
                row.append(item.get(f))
            rows.append(row)
            
        return fields, rows

    async def preview_data(self, entity_name: str, limit: int = 10) -> Tuple[List[str], List[List[Any]]]:
        # Execute query with default preview fields
        schema = await self.discover_schema()
        fields = []
        for ent in schema:
            if ent["physical_name"] == entity_name:
                fields = [f["physical_name"] for f in ent["fields"][:5]]
                break
        if not fields:
            fields = ["id", "name"]
            
        return await self.execute_query({
            "entity": entity_name,
            "fields": fields,
            "filters": [],
            "limit": limit
        })

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "rest_api",
            "name": "Generic REST API",
            "description": "Connects to arbitrary JSON REST APIs with OAuth2/Bearer, Basic Auth, or Custom Headers.",
            "required_credentials": ["base_url", "auth_type"],
            "supported_operations": ["filter", "limit"]
        }
