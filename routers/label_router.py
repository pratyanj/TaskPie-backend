from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.label_model import Label
from schemas.label_schame import LabelCreate, LabelUpdate
from auth.deps import get_current_user
from models.user_model import User

router = APIRouter(prefix="/labels", tags=["Labels"])

# CREATE
@router.post("/", response_model=Label)
def create_label(
    label: LabelCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    db_label = Label(**label.dict(), owner_id=current_user.id)
    session.add(db_label)
    session.commit()
    session.refresh(db_label)
    return db_label


# READ ALL
@router.get("/", response_model=list[Label])
def get_labels(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return session.exec(select(Label).where(Label.owner_id == current_user.id)).all()


# READ ONE
@router.get("/{label_id}", response_model=Label)
def get_label(
    label_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    label = session.exec(select(Label).where(Label.id == label_id, Label.owner_id == current_user.id)).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    return label


# UPDATE
@router.put("/{label_id}", response_model=Label)
def update_label(
    label_id: int,
    label_update: LabelUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    label = session.exec(select(Label).where(Label.id == label_id, Label.owner_id == current_user.id)).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")

    for key, value in label_update.dict(exclude_unset=True).items():
        setattr(label, key, value)

    session.add(label)
    session.commit()
    session.refresh(label)
    return label


# DELETE
@router.delete("/{label_id}")
def delete_label(
    label_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    label = session.exec(select(Label).where(Label.id == label_id, Label.owner_id == current_user.id)).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")

    session.delete(label)
    session.commit()
    return {"message": "Label deleted"}
