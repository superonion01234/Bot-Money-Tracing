import csv
from io import StringIO
from flask import Response
import requests

def export_csv(data):
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID','User ID','Jenis','Kategori','Jumlah/Gram','Tanggal','Catatan'])
    for t in data:
        if hasattr(t, "jumlah"):
            val = t.jumlah
        elif hasattr(t, "berat_gram"):
            val = t.berat_gram
        else:
            val = ""
        kategori = getattr(t, "kategori", "Emas" if hasattr(t,"berat_gram") else "")
        jenis = getattr(t,"jenis","Emas")
        cw.writerow([t.id, t.user_id, jenis, kategori, val, t.tanggal, t.note])
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment;filename=transaksi.csv"}
    )

def get_harga_emas_per_gram():
    try:
        data = requests.get("https://metals.live/api/spot").json()
        harga_emas_usd_per_oz = data[0]["gold"]
        usd_to_idr = 15500  # bisa diganti API kurs
        harga_per_gram_idr = harga_emas_usd_per_oz / 31.1035 * usd_to_idr
        return round(harga_per_gram_idr, 2)
    except Exception as e:
        print("Gagal mengambil harga emas:", e)
        return 1000000