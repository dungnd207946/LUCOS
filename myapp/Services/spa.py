from myapp.models import SpaCard, Card_Treatment, Treatment, SpaBooking, Khach_hang
from myapp.templates.config import db
def getAllCard():
    return SpaCard.query.all()

def getCardByCustomerID(customer_id):
    return SpaCard.query.filter(SpaCard.customer_id == customer_id).all()

def getTreatmentByCardID(card_id):
    treatmentByCard = (db.session.query(Card_Treatment.card_id,Card_Treatment.treatment_id, Card_Treatment.total_time, Card_Treatment.time_used, Card_Treatment.price, Treatment.name)
                       .filter(Card_Treatment.card_id == card_id)
                       .join(Treatment, Card_Treatment.treatment_id == Treatment.id)).all()
    return treatmentByCard

def getTreatmentByID(treatment_id):
    treatment = Treatment.query.filter(Treatment.id == treatment_id).first()
    return treatment

def getBookingByCardID(card_id):
    booking = db.session.query(SpaBooking.date, SpaBooking.status, Treatment.name).filter(SpaBooking.card_id == card_id).join(Treatment, SpaBooking.treatment_id == Treatment.id).all()
    return booking

def getSpaCardCustomer():
    customer = (db.session.query(SpaCard.id, SpaCard.total_price, SpaCard.debt, Khach_hang.ten_khach_hang,
                      Khach_hang.so_dien_thoai, Khach_hang.id.label('customer_id'))
                      .join(Khach_hang, SpaCard.customer_id == Khach_hang.id)
                )
    return customer