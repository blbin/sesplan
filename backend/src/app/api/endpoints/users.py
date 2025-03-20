from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, User
from app.crud.user import create_user, get_user, get_users, get_user_by_username
from app.core.security import get_current_active_user

# Use prefix but WITHOUT duplicating in the route paths
router = APIRouter(tags=["users"])


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    """Create new user"""
    # Check if username already exists
    existing_user = get_user_by_username(db, username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    return create_user(db=db, user=user)


@router.get("/", response_model=list[User])
def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Retrieve users"""
    return get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=User)
def read_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Get specific user by ID"""
    user = get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user