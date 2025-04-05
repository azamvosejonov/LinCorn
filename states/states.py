from aiogram.dispatcher.filters.state import StatesGroup, State

class next_quiz(StatesGroup):
    keyingi = State()
    keyingisi = State()
    tel = State()
    grux = State()
    status = State()

class oquvchi_qo(StatesGroup):
    ism = State()
    yosh = State()
    tel = State()
    gruhi = State()
    o_id = State()
    tanlash = State()

class oquvchi_o(StatesGroup):
    ism = State()
    grux_id = State()

class oquvchi_r(StatesGroup):
    grux_id = State()

class AddJadval(StatesGroup):
    title = State()
    start_time = State()
    end_time = State()
    date=State()

class UpdateJadval(StatesGroup):
    id = State()
    title = State()
    date = State()
    start_time = State()
    end_time = State()

class TolovStates(StatesGroup):
    amount = State()  # Payment amount
    payment_date = State()  # Payment date
    confirm = State()  # Payment confirmation

class Davomat(StatesGroup):
    grux_id = State()
    ism_familya = State()

class PaymentState(StatesGroup):
    amount = State()
    card_number = State()
    photo = State()

class SendMessageState(StatesGroup):
    waiting_for_message = State()
    waiting_for_group_message = State()
    waiting_for_all_message = State()

class PaymentStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_group_id = State()
    waiting_for_amount = State()
    waiting_for_date = State()

class AdminStates(StatesGroup):
    admin = State()


class PaymentAmountState(StatesGroup):
    waiting_for_amount = State()
