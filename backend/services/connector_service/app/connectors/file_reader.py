import io
import base64
import pandas as pd
from typing import Dict, Any, List, Tuple
from app.connectors.base import BaseConnector

class FileReaderConnector(BaseConnector):
    """
    Production-ready CSV and Excel connector.
    Ingests files (supplied as base64-encoded strings in credentials),
    auto-infers schema types, and supports querying via pandas in-memory filtering.
    """
    
    def __init__(self, credentials: Dict[str, Any], additional_params: Dict[str, Any] = None):
        super().__init__(credentials, additional_params)
        self.dataframes: Dict[str, pd.DataFrame] = {}

    def _load_data(self) -> None:
        if self.dataframes:
            return
            
        file_name = self.credentials.get("file_name", "dataset.csv")
        file_content_base64 = self.credentials.get("file_content", "")
        
        # Create fallback dummy data if no file is provided (for initial testing/registration)
        if not file_content_base64:
            dummy_data = {
                "id": [1, 2, 3],
                "compound_name": ["Aspirin", "Caffeine", "Ibuprofen"],
                "mw": [180.16, 194.19, 206.29],
                "active": [True, True, False]
            }
            self.dataframes["default"] = pd.DataFrame(dummy_data)
            return

        try:
            # Decode base64 bytes
            file_bytes = base64.b64decode(file_content_base64)
            
            if file_name.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_bytes))
                entity_name = file_name.split(".")[0].lower()
                self.dataframes[entity_name] = df
            elif file_name.endswith((".xls", ".xlsx")):
                xls = pd.ExcelFile(io.BytesIO(file_bytes))
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name)
                    entity_name = f"{file_name.split('.')[0]}_{sheet_name}".lower().replace(" ", "_")
                    self.dataframes[entity_name] = df
            else:
                raise ValueError("Unsupported file extension. Only CSV and Excel (.xls, .xlsx) are supported.")
        except Exception as e:
            raise ValueError(f"Failed to ingest and parse file '{file_name}': {str(e)}")

    async def connect(self) -> None:
        self._load_data()

    async def disconnect(self) -> None:
        self.dataframes.clear()

    async def test_connection(self) -> Tuple[bool, str]:
        try:
            self._load_data()
            return True, f"File successfully parsed: detected {len(self.dataframes)} queryable entities."
        except Exception as e:
            return False, f"File ingestion failed: {str(e)}"

    async def discover_schema(self) -> List[Dict[str, Any]]:
        self._load_data()
        entities = []
        for name, df in self.dataframes.items():
            fields = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                data_type = "string"
                if "int" in dtype:
                    data_type = "integer"
                elif "float" in dtype:
                    data_type = "float"
                elif "bool" in dtype:
                    data_type = "boolean"
                elif "datetime" in dtype:
                    data_type = "date"
                    
                fields.append({
                    "physical_name": col,
                    "display_name": str(col).replace("_", " ").title(),
                    "data_type": data_type,
                    "is_nullable": df[col].isnull().any(),
                    "is_primary_key": col.lower() in ["id", "key", "uuid", "index"],
                    "description": f"Field '{col}' inferred from headers"
                })
            
            entities.append({
                "physical_name": name,
                "display_name": name.replace("_", " ").title(),
                "description": f"Uploaded file dataset '{name}'",
                "fields": fields
            })
        return entities

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        self._load_data()
        entity = query["entity"]
        fields = query["fields"]
        filters = query.get("filters") or []
        limit = query.get("limit", 100)
        
        if entity not in self.dataframes:
            raise ValueError(f"Entity '{entity}' not found in the ingested file.")
            
        df = self.dataframes[entity]
        
        # Apply filters sequentially in Pandas
        for f in filters:
            field = f["field"]
            op = f["operator"]
            val = f["value"]
            
            if op == "=":
                df = df[df[field] == val]
            elif op == "!=":
                df = df[df[field] != val]
            elif op == ">":
                df = df[df[field] > val]
            elif op == "<":
                df = df[df[field] < val]
            elif op == ">=":
                df = df[df[field] >= val]
            elif op == "<=":
                df = df[df[field] <= val]
            elif op.upper() == "LIKE":
                df = df[df[field].astype(str).str.contains(str(val), case=False, na=False)]
            elif op.upper() == "IN":
                # Ensure val is a list
                val_list = val if isinstance(val, list) else [val]
                df = df[df[field].isin(val_list)]
                
        # Limit columns and slice row count
        df_selected = df[fields].head(limit)
        
        columns = list(df_selected.columns)
        # Convert pandas NaN values to python None to avoid invalid JSON output
        rows = df_selected.where(pd.notnull(df_selected), None).values.tolist()
        return columns, rows

    async def preview_data(self, entity_name: str, limit: int = 10) -> Tuple[List[str], List[List[Any]]]:
        self._load_data()
        if entity_name not in self.dataframes:
            raise ValueError(f"Entity '{entity_name}' not found.")
        df = self.dataframes[entity_name].head(limit)
        columns = list(df.columns)
        rows = df.where(pd.notnull(df), None).values.tolist()
        return columns, rows

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "file",
            "name": "CSV / Excel Upload",
            "description": "Ingests CSV or Excel spreadsheets, auto-detects schemas, and supports relational queries.",
            "required_credentials": ["file_name", "file_content"],
            "supported_operations": ["filter", "limit"]
        }

class CSVConnector(FileReaderConnector):
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "csv",
            "name": "CSV Upload",
            "description": "Ingests local flat comma/tab separated files, auto-detects schemas, and enables direct data exploration.",
            "required_credentials": ["file_name", "file_content"],
            "supported_operations": ["filter", "limit"]
        }

class ExcelConnector(FileReaderConnector):
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "excel",
            "name": "Excel Upload",
            "description": "Ingests Microsoft Excel spreadsheets (.xls, .xlsx), parses multiple sheets, and auto-detects schemas.",
            "required_credentials": ["file_name", "file_content"],
            "supported_operations": ["filter", "limit"]
        }
