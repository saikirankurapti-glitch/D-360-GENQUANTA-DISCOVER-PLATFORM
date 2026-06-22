from app.connectors.registry import ConnectorRegistry
from app.connectors.postgres import PostgreSQLConnector
from app.connectors.sqlserver import SQLServerConnector
from app.connectors.oracle import OracleConnector
from app.connectors.snowflake import SnowflakeConnector
from app.connectors.file_reader import FileReaderConnector, CSVConnector, ExcelConnector
from app.connectors.rest_api import RestApiConnector
from app.connectors.mongodb import MongoDBConnector
from app.connectors.enterprise.eln import ELNConnector
from app.connectors.enterprise.lims import LIMSConnector
from app.connectors.enterprise.assay import AssayConnector
from app.connectors.enterprise.registration import CompoundRegistrationConnector
from app.connectors.enterprise.inventory import InventoryConnector

# Automatically register all built-in and enterprise connectors
ConnectorRegistry.register("postgresql", PostgreSQLConnector)
ConnectorRegistry.register("sqlserver", SQLServerConnector)
ConnectorRegistry.register("oracle", OracleConnector)
ConnectorRegistry.register("snowflake", SnowflakeConnector)
ConnectorRegistry.register("file", FileReaderConnector)
ConnectorRegistry.register("csv", CSVConnector)
ConnectorRegistry.register("excel", ExcelConnector)
ConnectorRegistry.register("rest_api", RestApiConnector)
ConnectorRegistry.register("mongodb", MongoDBConnector)
ConnectorRegistry.register("eln", ELNConnector)
ConnectorRegistry.register("lims", LIMSConnector)
ConnectorRegistry.register("assay", AssayConnector)
ConnectorRegistry.register("registration", CompoundRegistrationConnector)
ConnectorRegistry.register("inventory", InventoryConnector)

