from sqlalchemy.orm import Session, joinedload
from ..models.world import World
from ..models.world_user import WorldUser, RoleEnum
from ..schemas.world import WorldCreate, WorldUpdate

def get_world(db: Session, world_id: int):
    return db.query(World).filter(World.id == world_id).first()

def get_worlds_by_owner(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get worlds where the user has the OWNER role."""
    # Najdeme asociace, kde je uživatel vlastníkem
    owner_associations = (
        db.query(WorldUser.world_id)
        .filter(WorldUser.user_id == user_id, WorldUser.role == RoleEnum.OWNER)
        .subquery()
    )
    # Vrátíme světy, jejichž ID jsou v seznamu vlastněných světů
    return (
        db.query(World)
        .filter(World.id.in_(owner_associations))
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_world(db: Session, world: WorldCreate, creator_id: int):
    """Creates a new world and assigns the creator as OWNER."""
    # Vytvoříme svět bez owner_id
    db_world = World(**world.dict())
    # Vytvoříme asociaci vlastníka
    owner_association = WorldUser(
        user_id=creator_id,
        world=db_world, # Předáme instanci pro automatické propojení
        role=RoleEnum.OWNER
    )
    db.add(db_world)
    db.add(owner_association)
    try:
        db.commit()
        db.refresh(db_world)
    except Exception as e:
        db.rollback()
        print(f"Error creating world or owner association: {e}")
        raise
    return db_world

def update_world(db: Session, db_world: World, world_in: WorldUpdate):
    """Updates a world. Assumes authorization check happened in the API layer."""
    update_data = world_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_world, key, value)
    db.add(db_world)
    db.commit()
    db.refresh(db_world)
    return db_world

def delete_world(db: Session, db_world: World):
    """Deletes a world. Assumes authorization check happened in the API layer."""
    db.delete(db_world)
    db.commit()
    # Vracíme smazaný objekt, i když už v DB není (pro response_model v API)
    return db_world