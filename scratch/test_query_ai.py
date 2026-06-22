import sys
import os

# Add paths so we can import app modules
sys.path.append(r"c:\Users\saiki\GENQUANTAA DISCOVER\backend\services\connector_service")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup environment for config loading
os.environ["DATABASE_URL"] = "postgresql://postgres:Saikiran%40123@localhost:5432/genquantaa_connector"
os.environ["ENCRYPTION_KEY"] = "351F6FEE44C2BD56A11D36982DB5F11F351F6FEE44C2BD56A11D36982DB5F11F"

from app.core.database import SessionLocal
from app.repositories.connector_repository import repo
from app.connectors.enterprise.eln import ELNConnector
import asyncio

async def main():
    db = SessionLocal()
    try:
        source_id = 5
        db_source = repo.get_data_source(db, source_id)
        credentials = repo.get_decrypted_credentials(db, source_id)
        add_params = db_source.config.additional_params if db_source.config else {}
        if isinstance(add_params, str):
            import json
            add_params = json.loads(add_params)
            
        print("Decrypted Credentials:", credentials)
        print("Additional Params:", add_params)
        
        # Initialize connector
        connector = ELNConnector(credentials, add_params)
        
        # Let's run execute_query
        query_payload = {
            "entity": "experiments",
            "fields": ["experiment_id", "title", "author", "status"],
            "limit": 5
        }
        cols, rows = await connector.execute_query(query_payload)
        print("Columns:", cols)
        print("Rows count:", len(rows))
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
