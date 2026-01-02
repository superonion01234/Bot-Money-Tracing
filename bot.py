import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from database import SessionLocal, engine
from models import Base, Transaksi, TargetMenabung, TransaksiEmas
from datetime import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.getenv("8424316759:AAHBGLJljd5UwBh7H1XRDnJfWRK76uTZRzM")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

Base.metadata.create_all(bind=engine)

kategori_map = {
    "Pengeluaran": ["Makan Pokok","Jajan","Transportasi","Top-up","Belanja Pokok",
                    "Tagihan Listrik","Tagihan WiFi","Tagihan Lingkungan","Laundry",
                    "Pulsa/Kuota","Sedekah"],
    "Pemasukan": ["Uang Makan","Gaji","Tukin/Remun","Bonus","Tak Terduga"],
    "Menabung": ["Anak","Kontrakan","Rumah","Haji","Dana Darurat"]
}

user_state = {}

# --- Input transaksi ---
@dp.message_handler(commands=["catat"])
async def start_input(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    for jenis in ["Pengeluaran","Pemasukan","Menabung"]:
        keyboard.add(InlineKeyboardButton(jenis, callback_data=f"jenis|{jenis}"))
    await message.answer("Pilih jenis transaksi:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("jenis|"))
async def pilih_jenis(callback_query: types.CallbackQuery):
    jenis = callback_query.data.split("|")[1]
    keyboard = InlineKeyboardMarkup()
    for k in kategori_map[jenis]:
        keyboard.add(InlineKeyboardButton(k, callback_data=f"kategori|{jenis}|{k}"))
    await bot.send_message(callback_query.from_user.id, f"Pilih kategori untuk {jenis}:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("kategori|"))
async def pilih_kategori(callback_query: types.CallbackQuery):
    _, jenis, kategori = callback_query.data.split("|")
    await bot.send_message(callback_query.from_user.id, f"Ketik jumlah nominal untuk {kategori} ({jenis}):")
    user_state[callback_query.from_user.id] = {"jenis": jenis, "kategori": kategori}

@dp.message_handler(lambda msg: user_state.get(msg.from_user.id, {}).get("jenis") in ["Pengeluaran","Pemasukan","Menabung"])
async def input_nominal(message: types.Message):
    state = user_state.get(message.from_user.id)
    if not state:
        return
    try:
        jumlah = float(message.text.replace(",", ""))
    except:
        await message.reply("Masukkan angka valid.")
        return

    db = SessionLocal()
    transaksi = Transaksi(
        user_id=str(message.from_user.id),
        jenis=state['jenis'],
        kategori=state['kategori'],
        jumlah=jumlah,
        tanggal=datetime.utcnow().date()
    )
    db.add(transaksi)
    db.commit()
    db.close()
    await message.reply(f"✅ Data tersimpan:\nJenis: {state['jenis']}\nKategori: {state['kategori']}\nJumlah: Rp{jumlah:,.0f}")
    user_state.pop(message.from_user.id)

# --- Target menabung ---
@dp.message_handler(commands=["target"])
async def set_target(message: types.Message):
    try:
        _, kategori, nominal = message.text.split(" ",2)
        nominal = float(nominal.replace(",",""))
    except:
        await message.reply("Format salah. Contoh: /target Rumah 20000000")
        return

    db = SessionLocal()
    existing = db.query(TargetMenabung).filter_by(user_id=str(message.from_user.id), kategori=kategori).first()
    if existing:
        existing.target = nominal
    else:
        db.add(TargetMenabung(user_id=str(message.from_user.id), kategori=kategori, target=nominal))
    db.commit()
    db.close()
    await message.reply(f"✅ Target tabungan '{kategori}' diset ke Rp{nominal:,.0f}")

# --- Menabung Emas ---
@dp.message_handler(commands=["emas"])
async def input_emas(message: types.Message):
    await message.reply("Masukkan jumlah emas yang ditabung (gram). Contoh: 1.25")
    user_state[message.from_user.id] = {"jenis": "Emas"}

@dp.message_handler(lambda msg: user_state.get(msg.from_user.id, {}).get("jenis") == "Emas")
async def save_emas(message: types.Message):
    try:
        berat = float(message.text.replace(",", "."))
    except:
        await message.reply("Masukkan angka valid, contoh: 0.5 atau 2.75")
        return

    db = SessionLocal()
    transaksi = TransaksiEmas(user_id=str(message.from_user.id), berat_gram=berat, tanggal=datetime.utcnow().date())
    db.add(transaksi)
    db.commit()
    db.close()
    await message.reply(f"✅ Disimpan: {berat} gram emas.")
    user_state.pop(message.from_user.id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
