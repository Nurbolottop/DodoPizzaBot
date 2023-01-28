from aiogram import Bot,Dispatcher,types,executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
import config
import sqlite3
import logging
import datetime

bot = Bot(config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)


start_connect = sqlite3.connect('users.db')
cur  = start_connect.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(255),
    chat_id INTEGER,
    phone_number INTEGER
    );
    """)

cur.execute("""CREATE TABLE  IF NOT EXISTS orders(
    title VARCHAR(255),
    address VARCHAR(255),
    date_time_order  VARCHAR(255)
    
    );
    """)

cur.execute("""CREATE TABLE  IF NOT EXISTS address(
    id_user INTEGER,
    address_longitude INTEGER,
    address_latitude INTEGER
    
    );
    """)
start_connect.commit()

inline_kb = [
        [InlineKeyboardButton("Отправить контакт", request_contact=True)],
        [InlineKeyboardButton("Отправитьлокацию",request_location=True)],
        [InlineKeyboardButton("Заказать еду!", callback_data = "Заказать еду!")],
    ]
inline_keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)

kb = [
    [KeyboardButton("Отправить контакт", request_contact=True)],
    [KeyboardButton("Заказать еду!")],
    
    [KeyboardButton("Отправитьлокацию", request_location=True)]
]
keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True,)


    
@dp.message_handler(commands=["start"])
async def start(message : types.Message):

    # try:
        cur  = start_connect.cursor()
        cur.execute(f"SELECT chat_id FROM users WHERE  chat_id  == {message.from_user.id};")
        result = cur.fetchall()
        if result ==[]:
            cur.execute(f"INSERT INTO users (first_name, last_name, username, chat_id, )VALUES ('{message.from_user.first_name}',  '{message.from_user.last_name}','{message.from_user.username}',{message.chat.id},);")
            start_connect.commit()
        await message.answer(f"Здравстуйте ,{message.from_user.full_name}. Вас приветствует администрация Geektech.\nЕсли хотите узнать обо мне больше нажмите: /help ", reply_markup=keyboard)
        await message.answer("Вот что я могу", reply_markup=inline_keyboard)
        
    # except:
    #     await message.answer("Вышли не большие ошибки обратитесь тех.админу: ")

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def get_contact(msg:types.Message):
    
        await msg.reply("OK")
        cur.execute(f"UPDATE users SET phone_number = {msg.contact['phone_number']} WHERE (chat_id = {msg.from_user.id});")
        start_connect.commit()
        
@dp.message_handler(content_types=types.ContentType.LOCATION)
async def get_location(msg:types.Message):
    
    cur.execute(f"INSERT INTO address (id_user, address_longitude, address_latitude) VALUES ({msg.from_user.id}, {msg.location['latitude']}, {msg.location['longitude']});")
    start_connect.commit()
    await msg.reply("OK")

class ContactForm(StatesGroup):
    client = State()

@dp.message_handler(text = "Заказать еду!")
async def start(message : types.Message):
    await message.answer("Введите ваш заказ следующим образом: ")
    await message.reply("Еда, Адрес")
    await ContactForm.client.set()
    

@dp.message_handler(state=ContactForm.client)
async def get_contact(message: types.Message, state: FSMContext):
    # try:
        times = datetime.datetime.now()
        
        cur_contact = start_connect.cursor()
        res = message.text.replace(',', '',).split()
        cur_contact = cur_contact.execute(f"INSERT INTO orders (title, address, date_time_order) VALUES ('{res[0]}', '{res[1]}','{times}');")
        start_connect.commit()
        await state.finish()
    # except:
    #     await message.answer("Вышли не большие ошибки обратитесь тех.админу: @erk1nbaew")
        
executor.start_polling(dp)
