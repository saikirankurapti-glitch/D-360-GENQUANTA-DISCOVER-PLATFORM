from typing import Dict, Any, List, Tuple
from sqlalchemy import create_engine, inspect, text
from app.connectors.base import BaseConnector

class OracleConnector(BaseConnector):
    """
    Production-ready Oracle Database connector using SQLAlchemy and oracledb thin driver.
    """
    
    def __init__(self, credentials: Dict[str, Any], additional_params: Dict[str, Any] = None):
        super().__init__(credentials, additional_params)
        self.engine = None

    async def connect(self) -> None:
        if not self.engine:
            host = self.credentials.get("host")
            port = self.credentials.get("port", 1521)
            username = self.credentials.get("username")
            password = self.credentials.get("password")
            
            # Oracle SID or Service Name
            service_name = self.credentials.get("service_name")
            sid = self.credentials.get("sid")
            
            if not all([host, username, password]) or not (service_name or sid):
                raise ValueError("Incomplete credentials. host, username, password, and (service_name or sid) are required.")
                
            # Construct Oracle connection string
            if service_name:
                db_url = f"oracle+oracledb://{username}:{password}@{host}:{port}/?service_name={service_name}"
            else:
                db_url = f"oracle+oracledb://{username}:{password}@{host}:{port}/?sid={sid}"
                
            self.engine = create_engine(
                db_url,
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
                conn.execute(text("SELECT 1 FROM DUAL"))
            return True, "Successfully connected to Oracle Database."
        except Exception as e:
            return False, f"Oracle connection failed: {str(e)}"

    async def discover_schema(self) -> List[Dict[str, Any]]:
        await self.connect()
        # In Oracle, schema usually defaults to the uppercase username
        schema_name = self.additional_params.get("schema", self.credentials.get("username", "")).upper()
        
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
                    if "number" in type_str:
                        # Inspect precision/scale to differentiate float vs integer
                        data_type = "integer" if "scale=0" in type_str or "," not in type_str else "float"
                    elif "float" in type_str or "double" in type_str:
                        data_type = "float"
                    elif "char" in type_str or "varchar" in type_str or "clob" in type_str:
                        data_type = "string"
                    elif "date" in type_str or "timestamp" in type_str:
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
                    "description": f"Oracle table '{table}'",
                    "fields": fields
                })
        return entities

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        await self.connect()
        entity = query["entity"]
        fields = query["fields"]
        filters = query.get("filters") or []
        limit = query.get("limit", 100)
        
        schema_name = self.additional_params.get("schema", self.credentials.get("username", "")).upper()
        
        # Oracle LIMIT syntax is FETCH FIRST n ROWS ONLY (for 12c+)
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
            
        sql_query += f" FETCH FIRST {limit} ROWS ONLY"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query), params)
            columns = list(result.keys())
            rows = [list(r) for r in result.fetchall()]
            return columns, rows

    async def preview_data(self, entity_name: str, limit: int = 10) -> Tuple[List[str], List[List[Any]]]:
        await self.connect()
        schema_name = self.additional_params.get("schema", self.credentials.get("username", "")).upper()
        sql_query = f'SELECT * FROM "{schema_name}"."{entity_name}" FETCH FIRST {limit} ROWS ONLY'
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query))
            columns = list(result.keys())
            rows = [list(r) for r in result.fetchall()]
            return columns, rows

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "oracle",
            "name": "Oracle Database",
            "description": "Connects to Oracle Databases using SQLAlchemy and oracledb thin client",
            "required_credentials": ["host", "port", "username", "password", "service_name"],
            "supported_operations": ["filter", "limit", "sort", "joins"]
        }
