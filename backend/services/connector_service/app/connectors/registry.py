from typing import Dict, Type, List, Any
from .base import BaseConnector

class ConnectorRegistry:
    """
    Singleton-style class to manage registration and instantiation of connector plugins.
    Allows for dynamic discovery of supported data sources.
    """
    
    _registry: Dict[str, Type[BaseConnector]] = {}

    @classmethod
    def register(cls, connector_type: str, connector_class: Type[BaseConnector]) -> None:
        """
        Registers a new connector class under a specific connector_type.
        """
        cls._registry[connector_type.lower()] = connector_class
        print(f"Registered connector: {connector_type}")

    @classmethod
    def get_connector(cls, connector_type: str) -> Type[BaseConnector]:
        """
        Retrieves the connector class for the given type.
        Raises ValueError if not registered.
        """
        connector_type_lower = connector_type.lower()
        if connector_type_lower not in cls._registry:
            raise ValueError(f"No connector registered for type: {connector_type}")
        return cls._registry[connector_type_lower]

    @classmethod
    def get_all_capabilities(cls) -> List[Dict[str, Any]]:
        """
        Returns capabilities info for all registered connectors.
        """
        capabilities = []
        for connector_type, connector_class in cls._registry.items():
            try:
                # Instantiate with dummy configuration to retrieve capabilities
                instance = connector_class(credentials={}, additional_params={})
                capabilities.append(instance.get_capabilities())
            except Exception as e:
                # Fallback if instantiation fails
                capabilities.append({
                    "connector_type": connector_type,
                    "name": connector_type.capitalize(),
                    "description": f"Connector for {connector_type}",
                    "required_credentials": [],
                    "supported_operations": []
                })
        return capabilities

    @classmethod
    def clear(cls) -> None:
        """Clears registry (useful for testing)."""
        cls._registry.clear()
