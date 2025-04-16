from sqlalchemy.orm import Session
from ..models.world import World
from ..schemas.world import WorldCreate, WorldUpdate

def get_world(db: Session, world_id: int):
    return db.query(World).filter(World.id == world_id).first()

def get_worlds_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(World).filter(World.owner_id == owner_id).offset(skip).limit(limit).all()

def create_world(db: Session, world: WorldCreate, owner_id: int):
    db_world = World(**world.dict(), owner_id=owner_id)
    db.add(db_world)
    db.commit()
    db.refresh(db_world)
    return db_world

def update_world(db: Session, db_world: World, world_in: WorldUpdate):
    update_data = world_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_world, key, value)
    db.add(db_world)
    db.commit()
    db.refresh(db_world)
    return db_world

def delete_world(db: Session, db_world: World):
    db.delete(db_world)
    db.commit()
    return db_world 