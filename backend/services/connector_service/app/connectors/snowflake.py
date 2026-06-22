from typing import Dict, Any, List, Tuple
from sqlalchemy import create_engine, inspect, text
from app.connectors.base import BaseConnector

class SnowflakeConnector(BaseConnector):
    """
    Production-ready Snowflake connector using SQLAlchemy and snowflake-connector-python.
    """
    
    def __init__(self, credentials: Dict[str, Any], additional_params: Dict[str, Any] = None):
        super().__init__(credentials, additional_params)
        self.engine = None

    async def connect(self) -> None:
        if not self.engine:
            account = self.credentials.get("account")
            username = self.credentials.get("username")
            password = self.credentials.get("password")
            database = self.credentials.get("database")
            schema = self.credentials.get("schema", "PUBLIC")
            warehouse = self.credentials.get("warehouse")
            role = self.credentials.get("role")
            
            if not all([account, username, password, database]):
                raise ValueError("Incomplete credentials. account, username, password, and database are required.")
                
            # Construct Snowflake connection URL
            db_url = f"snowflake://{username}:{password}@{account}/{database}/{schema}"
            
            # Append optional params
            query_params = []
            if warehouse:
                query_params.append(f"warehouse={warehouse}")
            if role:
                query_params.append(f"role={role}")
                
            if query_params:
                db_url += "?" + "&".join(query_params)
                
            self.engine = create_engine(db_url, pool_pre_ping=True)

    async def disconnect(self) -> None:
        if self.engine:
            self.engine.dispose()
            self.engine = None

    async def test_connection(self) -> Tuple[bool, str]:
        try:
            await self.connect()
            with self.engine.connect() as conn:
                conn.execute(text("SELECT CURRENT_VERSION()"))
            return True, "Successfully connected to Snowflake."
        except Exception as e:
            return False, f"Snowflake connection failed: {str(e)}"

    async def discover_schema(self) -> List[Dict[str, Any]]:
        await self.connect()
        schema_name = self.credentials.get("schema", "PUBLIC").upper()
        
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
                    type_str = str(col["type"]).lower()
                    data_type = "string"
                    if "number" in type_str or "integer" in type_str or "int" in type_str:
                        # Precision check
                        data_type = "integer" if "scale=0" in type_str or "," not in type_str else "float"
                    elif "float" in type_str or "double" in type_str or "real" in type_str:
                        data_type = "float"
                    elif "boolean" in type_str or "bool" in type_str:
                        data_type = "boolean"
                    elif "date" in type_str or "timestamp" in type_str or "time" in type_str:
                        data_type = "date"
                        
                    fields.append({
                        "physical_name": col["name"],
                        "display_name": col["name"].replace("_", " ").title(),
                        "data_type": data_type,
                        "is_nullable": col["nullable"],
                        "is_primary_key": col["name"] in pk_cols,
                        "description": col.get("comment", "") or f"Field {col['name']}"
                    })
                
                entities.append({
                    "physical_name": table,
                    "display_name": table.replace("_", " ").title(),
                    "description": f"Snowflake table '{table}'",
                    "fields": fields
                })
        return entities

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        await self.connect()
        entity = query["entity"]
        fields = query["fields"]
        filters = query.get("filters") or []
        limit = query.get("limit", 100)
        
        schema_name = self.credentials.get("schema", "PUBLIC").upper()
        
        # Snowflake escaping requires double quotes for case sensitivity or exact matches
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
        schema_name = self.credentials.get("schema", "PUBLIC").upper()
        sql_query = f'SELECT * FROM "{schema_name}"."{entity_name}" LIMIT {limit}'
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query))
            columns = list(result.keys())
            rows = [list(r) for r in result.fetchall()]
            return columns, rows

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "snowflake",
            "name": "Snowflake Data Warehouse",
            "description": "Connects to Snowflake Cloud Data Warehouses using standard SQLAlchemy",
            "required_credentials": ["account", "username", "password", "database", "warehouse"],
            "supported_operations": ["filter", "limit", "sort", "joins"]
        }
