from fastapi import APIRouter, HTTPException, status, Depends
from app.models.admin_model import AdminCreate, AdminLogin
from app.core.security import hash_password, verify_password, create_access_token, oauth2_scheme, decode_token
from app.core.database import db
from datetime import timedelta
from app.core.security import get_current_admin
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"])
admins_collection = db["admins"]

@router.post("/register")
def register_admin(admin: AdminCreate):
    """
    One-time use route — manually create an admin.
    Disable or secure after first admin creation.
    """
    existing = admins_collection.find_one({"email": admin.email})
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")

    hashed_pw = hash_password(admin.password)
    admin_doc = {
        "email": admin.email,
        "password": hashed_pw,
        "full_name": admin.full_name or "",
    }
    admins_collection.insert_one(admin_doc)
    return {"message": "Admin registered successfully"}

@router.get("/me")
def get_current_admin_info(current_admin: str = Depends(get_current_admin)):
    """Get current admin's information."""
    db_admin = admins_collection.find_one({"email": current_admin})
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return {
        "email": db_admin.get("email"),
        "full_name": db_admin.get("full_name", ""),
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_admin = admins_collection.find_one({"email": form_data.username})
    if not db_admin or not verify_password(form_data.password, db_admin["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": form_data.username}, expires_delta=timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/test-protected")
def test_protected(current_admin: str = Depends(get_current_admin)):
    return {"message": f"Hello {current_admin}, you're authenticated!"}