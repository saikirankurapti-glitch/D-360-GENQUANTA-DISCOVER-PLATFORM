from sqlalchemy.orm import Session
from ..models.rbac import Role, Permission
from ..models.user import User
from ..core.security import get_password_hash

def seed_rbac(db: Session):
    # 1. Define permissions list
    permissions_list = [
        {"name": "admin_config", "description": "System admin config actions"},
        {"name": "run_queries", "description": "Run and execute analytical queries"},
        {"name": "edit_metadata", "description": "Edit or register metadata definitions"},
        {"name": "edit_connectors", "description": "Create and edit data source connectors"},
        {"name": "export_data", "description": "Export datasets to files (CSV/Excel/PDF)"},
        {"name": "approve_data", "description": "E-sign query, dataset, metadata approvals"},
        {"name": "view_audit_trail", "description": "Read and check database audit trail reports"}
    ]
    
    db_perms = {}
    for p in permissions_list:
        db_p = db.query(Permission).filter(Permission.name == p["name"]).first()
        if not db_p:
            db_p = Permission(name=p["name"], description=p["description"])
            db.add(db_p)
            db.flush()
        db_perms[p["name"]] = db_p

    # 2. Define roles and their permitted permission names
    roles_list = [
        {
            "name": "Admin",
            "description": "Administrator with full system privileges",
            "perms": ["admin_config", "run_queries", "edit_metadata", "edit_connectors", "export_data", "approve_data", "view_audit_trail"]
        },
        {
            "name": "Scientist",
            "description": "Scientific investigator performing query and compound analytics",
            "perms": ["run_queries", "edit_metadata", "export_data"]
        },
        {
            "name": "Reviewer",
            "description": "Validator responsible for signing off datasets and metadata modifications",
            "perms": ["run_queries", "approve_data"]
        },
        {
            "name": "Compliance Officer",
            "description": "Audit inspector reviewing system logs and database integrity reports",
            "perms": ["view_audit_trail"]
        }
    ]

    for r in roles_list:
        db_r = db.query(Role).filter(Role.name == r["name"]).first()
        if not db_r:
            db_r = Role(name=r["name"], description=r["description"])
            db.add(db_r)
            db.flush()
        
        # Link permissions to role
        db_r.permissions = [db_perms[pname] for pname in r["perms"]]
        db.add(db_r)

    db.commit()

    # 3. Create default bootstrapper accounts if they don't exist yet
    default_users = [
        {"email": "admin@genquantaa.com", "name": "System Administrator", "role_name": "Admin"},
        {"email": "scientist@genquantaa.com", "name": "Lead Researcher", "role_name": "Scientist"},
        {"email": "reviewer@genquantaa.com", "name": "Quality Reviewer", "role_name": "Reviewer"},
        {"email": "compliance@genquantaa.com", "name": "Compliance Inspector", "role_name": "Compliance Officer"}
    ]

    for u in default_users:
        db_u = db.query(User).filter(User.email == u["email"]).first()
        if not db_u:
            # Create user
            db_u = User(
                email=u["email"],
                hashed_password=get_password_hash("GenQuantaaDiscover2026!"),
                full_name=u["name"],
                role=u["role_name"],
                is_active=True
            )
            db.add(db_u)
            db.flush()
        
        # Check if user has the role assigned in user_roles link table
        role_obj = db.query(Role).filter(Role.name == u["role_name"]).first()
        if role_obj and role_obj not in db_u.roles:
            db_u.roles.append(role_obj)
            db.add(db_u)

    db.commit()
