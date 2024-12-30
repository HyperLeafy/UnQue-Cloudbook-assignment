from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import User, Availability, Appointment, session_local
from app.routes.auth import get_db, get_curr_user, DesignationStateEnum
from typing import List

router = APIRouter()

# setting up routes for professor
@router.post("/as")
def testsss():
    return {"message":"routeworks"}

# routes to check for profesor availablity and set it
@router.post("/availability")
def set_availability(time_slots: List[str], db: Session = Depends(get_db), curr_user: User = Depends(get_curr_user)):
    if curr_user.designation != DesignationStateEnum.PROFESSOR:
        raise HTTPException(status_code=403, detail="Not authorized")
    for time_slot in time_slots:
        new_availability = Availability(professor_id=curr_user.id, time_slot=time_slot)
        db.add(new_availability)
    db.commit()
    return {"message":"Availability added successfully"}


# routes remove availability
@router.delete("/appointment/{appointment_id}")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db), curr_user: User = Depends(get_curr_user)):
    if curr_user.designation != DesignationStateEnum.PROFESSOR:
        raise HTTPException(status_code=403, detail="Not authorized")
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.professor_id == curr_user.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found!!")
    db.delete(appointment)
    db.commit()
    return {"message": "Appointment canceled"}

        
    