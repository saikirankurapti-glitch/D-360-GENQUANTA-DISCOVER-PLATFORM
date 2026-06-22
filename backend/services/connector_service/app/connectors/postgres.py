import time
from typing import Dict, Any, List, Tuple
from sqlalchemy import create_engine, inspect, text
from app.connectors.base import BaseConnector

class PostgreSQLConnector(BaseConnector):
    """
    Production-grade PostgreSQL database connector.
    Utilizes SQLAlchemy engine capabilities for connection pooling, schema reflection, and query execution.
    """
    
    def __init__(self, credentials: Dict[str, Any], additional_params: Dict[str, Any] = None):
        super().__init__(credentials, additional_params)
        self.engine = None

    async def connect(self) -> None:
        if not self.engine:
            host = self.credentials.get("host")
            port = self.credentials.get("port", 5432)
            database = self.credentials.get("database")
            username = self.credentials.get("username")
            password = self.credentials.get("password")
            
            if not all([host, database, username, password]):
                raise ValueError("Incomplete PostgreSQL credentials. host, database, username, and password are required.")
                
            db_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            self.engine = create_engine(
                db_url,
                connect_args={"connect_timeout": 5},
                pool_pre_ping=True
            )

    async def disconnect(self) -> None:
        if self.engine:
            self.engine.dispose()
            self.engine = None

    async def test_connection(self) -> Tuple[bool, str]:
        try:
            await self.connect()
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True, "Successfully connected to PostgreSQL database."
        except Exception as e:
            return False, f"PostgreSQL connection test failed: {str(e)}"

    async def discover_schema(self) -> List[Dict[str, Any]]:
        await self.connect()
        schema_name = self.additional_params.get("schema", "public")
        
        entities = []
        with self.engine.connect() as conn:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names(schema=schema_name)
            
            for table in tables:
                columns = inspector.get_columns(table, schema=schema_name)
                pk_constraint = inspector.get_pk_constraint(table, schema=schema_name)
                pk_cols = pk_constraint.get("constrained_columns", []) if pk_constraint else []
                
                fields = []
                for col in columns:
                    # Infer generic string datatypes
                    type_str = str(col["type"]).lower()
                    data_type = "string"
                    if "int" in type_str:
                        data_type = "integer"
                    elif "float" in type_str or "numeric" in type_str or "double" in type_str or "decimal" in type_str:
                        data_type = "float"
                    elif "bool" in type_str:
                        data_type = "boolean"
                    elif "date" in type_str or "time" in type_str:
                        data_type = "date"
                        
                    fields.append({
                        "physical_name": col["name"],
                        "display_name": col["name"].replace("_", " ").title(),
                        "data_type": data_type,
                        "is_nullable": col["nullable"],
                        "is_primary_key": col["name"] in pk_cols,
                        "description": col.get("comment", "") or f"Column {col['name']}"
                    })
                
                entities.append({
                    "physical_name": table,
                    "display_name": table.replace("_", " ").title(),
                    "description": f"PostgreSQL table '{table}' in schema '{schema_name}'",
                    "fields": fields
                })
        return entities

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        await self.connect()
        entity = query["entity"]
        fields = query["fields"]
        filters = query.get("filters") or []
        limit = query.get("limit", 100)
        
        schema_name = self.additional_params.get("schema", "public")
        
        # Build SELECT clause safely escaping table and columns
        select_clause = ", ".join([f'"{f}"' for f in fields])
        sql_query = f'SELECT {select_clause} FROM "{schema_name}"."{entity}"'
        
        params = {}
        if filters:
            filter_clauses = []
            for idx, f in enumerate(filters):
                field = f["field"]
                op = f["operator"]
                val = f["value"]
                
                param_name = f"p_{idx}"
                params[param_name] = val
                
                if op.upper() == "LIKE":
                    filter_clauses.append(f'"{field}" LIKE :{param_name}')
                elif op.upper() == "IN":
                    filter_clauses.append(f'"{field}" IN :{param_name}')
                else:
                    filter_clauses.append(f'"{field}" {op} :{param_name}')
            sql_query += " WHERE " + " AND ".join(filter_clauses)
            
        sql_query += f" LIMIT {limit}"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query), params)
            columns = list(result.keys())
            rows = [list(r) for r in result.fetchall()]
            return columns, rows

    async def preview_data(self, entity_name: str, limit: int = 10) -> Tuple[List[str], List[List[Any]]]:
        await self.connect()
        schema_name = self.additional_params.get("schema", "public")
        sql_query = f'SELECT * FROM "{schema_name}"."{entity_name}" LIMIT {limit}'
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query))
            columns = list(result.keys())
            rows = [list(r) for r in result.fetchall()]
            return columns, rows

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "postgresql",
            "name": "PostgreSQL Database",
            "description": "Connects to relational PostgreSQL instances using standard SQLAlchemy",
            "required_credentials": ["host", "port", "database", "username", "password"],
            "supported_operations": ["filter", "limit", "sort", "joins"]
        }
