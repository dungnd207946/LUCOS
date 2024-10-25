from myapp.models import SpaCard, Card_Treatment, Treatment, SpaBooking, Khach_hang, User_account, Mask
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

def getAllTreatments():
    return Treatment.query.all()

def getAllBookingData():
    result = (db.session.query(SpaBooking, User_account, SpaCard, Khach_hang, Treatment, Mask)
              .join(User_account, SpaBooking.staff_id == User_account.id)
              .join(SpaCard, SpaBooking.card_id == SpaCard.id)
              .join(Khach_hang, SpaCard.customer_id == Khach_hang.id)
              .join(Treatment, SpaBooking.treatment_id == Treatment.id)
              .join(Mask, SpaBooking.mask_id == Mask.id)
              .all())
    booking_data = [
        {'id': booking.id,
         'staff_id': staff.id,
         'staff_name': staff.full_name,
         'treatment_name': treatment.name,
         'duration': treatment.duration,
         'customer_id': customer.id,
         'customer_name': customer.ten_khach_hang,
         'date': booking.date,
         'mask_id': mask.id,
         'mask': mask.mask_name,
         'note': booking.note,
         'customer_demand': booking.customer_demand,
         'status': booking.status,
         'is_new_customer': booking.is_new_customer}
        for booking, staff, card, customer, treatment, mask in result]
    return booking_data

def getCustomerCardDetail(number=None):
    if number is None:
        result = (db.session.query(Khach_hang.id.label('id'), Khach_hang.ten_khach_hang, SpaCard.id.label('card_id'), Treatment.name, Card_Treatment.total_time, Card_Treatment.time_used)
                  .join(SpaCard, Khach_hang.id == SpaCard.customer_id)
                  .join(Card_Treatment, SpaCard.id == Card_Treatment.card_id)
                  .join(Treatment, Card_Treatment.treatment_id == Treatment.id)
                  )
    else:
        result = (db.session.query(Khach_hang.id.label('id'), Khach_hang.ten_khach_hang, SpaCard.id.label('card_id'), Treatment.name, Card_Treatment.total_time,
                                   Card_Treatment.time_used)
                  .join(SpaCard, Khach_hang.id == SpaCard.customer_id)
                  .join(Card_Treatment, SpaCard.id == Card_Treatment.card_id)
                  .join(Treatment, Card_Treatment.treatment_id == Treatment.id)
                  .filter(Card_Treatment.total_time - Card_Treatment.time_used <= number)
                  )
    return result