from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

class BaseConnector(ABC):
    """
    Abstract Base Class defining the contract for all data source connectors.
    Each connector plugin must inherit from this and implement all abstract methods.
    """
    
    def __init__(self, credentials: Dict[str, Any], additional_params: Dict[str, Any] = None):
        self.credentials = credentials
        self.additional_params = additional_params or {}

    @abstractmethod
    async def connect(self) -> None:
        """
        Establishes a connection to the remote data source.
        Raises an exception if connection fails.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Closes the active connection and releases system resources.
        """
        pass

    @abstractmethod
    async def test_connection(self) -> Tuple[bool, str]:
        """
        Tests whether a connection can be established with the current credentials.
        Returns a tuple of (success: bool, message: str).
        """
        pass

    @abstractmethod
    async def discover_schema(self) -> List[Dict[str, Any]]:
        """
        Discovers database tables or endpoints (entities) and columns (fields).
        Returns a structured schema list:
        [
            {
                "physical_name": "table_name",
                "display_name": "Readable Name",
                "description": "Description of table",
                "fields": [
                    {
                        "physical_name": "column_name",
                        "display_name": "Readable Column Name",
                        "data_type": "string|integer|float|date|boolean",
                        "is_nullable": True/False,
                        "is_primary_key": True/False,
                        "description": "Column description"
                    }
                ]
            }
        ]
        """
        pass

    @abstractmethod
    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        """
        Executes a query using the structured query dictionary containing:
        - entity: Physical name of the table or endpoint.
        - fields: List of physical field names to fetch.
        - filters: List of filter dicts (field, operator, value).
        - limit: Maximum number of rows to return.
        
        Returns a tuple of (columns: List[str], rows: List[List[Any]]).
        """
        pass

    @abstractmethod
    async def preview_data(self, entity_name: str, limit: int = 10) -> Tuple[List[str], List[List[Any]]]:
        """
        Fetches a raw preview of an entity.
        Returns a tuple of (columns: List[str], rows: List[List[Any]]).
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Returns metadata about the connector's capabilities, description, and required parameters.
        Example:
        {
            "connector_type": "postgresql",
            "name": "PostgreSQL Database",
            "description": "Connects to relational PostgreSQL instances",
            "required_credentials": ["host", "port", "database", "username", "password"],
            "supported_operations": ["filter", "limit", "sort", "joins"]
        }
        """
        pass
