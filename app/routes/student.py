from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import User, Availability, Appointment, session_local
from app.routes.auth import get_db, get_curr_user, DesignationStateEnum
from pydantic import BaseModel
router = APIRouter()

class AppointmentBooking(BaseModel):
    professor_id: int
    time_slot: str
    

# setting routes for student

# route to check slot available
@router.get("/availability/{professor_id}")
def view_availability(professor_id: int, db: Session= Depends(get_db)):
    availability = db.query(Availability).filter(Availability.professor_id == professor_id).all()
    if not availability:
        raise HTTPException(status_code=400, detail="No slot available for thsi professor")
    return {"professor_id":professor_id, "available_slots":[slot.time_slot for slot in availability]}

# route to book an appointment
@router.post("/appointment")
def book_appointment(booking_data: AppointmentBooking, db: Session = Depends(get_db), curr_user: User = Depends(get_curr_user)):
    professor_id = booking_data.professor_id
    time_slot = booking_data.time_slot
    
    if curr_user.designation != DesignationStateEnum.STUDENT:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing_availability  = db.query(Availability).filter(Availability.professor_id == professor_id, Availability.time_slot == time_slot ).first()
    if not existing_availability:
        raise HTTPException(status_code=400, detail= "No slots available")
    
    existing_appointment = db.query(Appointment).filter(Appointment.professor_id == professor_id, Appointment.student_id == curr_user.id, Appointment.time_slot == time_slot).first()
    if existing_appointment:
        raise HTTPException(status_code=400, detail="You have already booked an apointment")
    
    new_appointment = Appointment(professor_id=professor_id, student_id=curr_user.id, time_slot=time_slot)
    db.add(new_appointment)
    db.commit()
    return {"message": "Appointment booked successfully"}

@router.get("/appointment")
def view_appointment(curr_user:User = Depends(get_curr_user), db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.student_id == curr_user.id).all()
    if not appointment:
        raise HTTPException(status_code=400, detail="No appoints have been made!")
    return {"student_id":curr_user.id, "appointment":[slot.time_slot for slot in appointment]}


