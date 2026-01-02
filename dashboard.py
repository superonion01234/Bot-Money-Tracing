from flask import Flask, render_template, request, redirect, url_for, session
from database import SessionLocal, engine
from models import Base, Transaksi, TargetMenabung, TransaksiEmas
from utils import export_csv, get_harga_emas_per_gram
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "290525")
PIN = os.getenv("DASHBOARD_PIN", "290525")

Base.metadata.create_all(bind=engine)

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        pin = request.form.get("pin")
        if pin==PIN:
            session['auth']=True
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="PIN salah")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("auth"):
        return redirect(url_for("login"))

    start_date = request.args.get("start")
    end_date = request.args.get("end")

    db = SessionLocal()
    query = db.query(Transaksi)
    if start_date:
        query = query.filter(Transaksi.tanggal >= datetime.fromisoformat(start_date).date())
    if end_date:
        query = query.filter(Transaksi.tanggal <= datetime.fromisoformat(end_date).date())
    data = query.all()

    # Chart data
    chart_data = {}
    for t in data:
        chart_data[t.kategori] = chart_data.get(t.kategori,0) + float(t.jumlah)

    # Progress Menabung
    targets = db.query(TargetMenabung).all()
    progress=[]
    for t in targets:
        total = db.query(Transaksi).filter(Transaksi.kategori==t.kategori, Transaksi.jenis=="Menabung").with_entities(Transaksi.jumlah).all()
        total_sum = sum([float(x[0]) for x in total])
        percent = (total_sum/float(t.target)*100) if t.target else 0
        progress.append({"kategori":t.kategori,"total":total_sum,"target":float(t.target),"percent":round(percent,2)})
    db.close()

    # Tabungan Emas
    db_emas=SessionLocal()
    transaksi_emas=db_emas.query(TransaksiEmas).all()
    db_emas.close()
    total_gram=sum([float(t.berat_gram) for t in transaksi_emas])
    harga_emas=get_harga_emas_per_gram()
    nilai_total_emas=total_gram*harga_emas

    return render_template("dashboard.html",
        data=data,
        chart_data=chart_data,
        start_date=start_date,
        end_date=end_date,
        progress=progress,
        total_gram=total_gram,
        harga_emas=harga_emas,
        nilai_total_emas=nilai_total_emas
    )

@app.route("/export_csv")
def export_csv_route():
    if not session.get("auth"):
        return redirect(url_for("login"))
    db=SessionLocal()
    data=db.query(Transaksi).all()+db.query(TransaksiEmas).all()
    db.close()
    return export_csv(data)

@app.route("/ping")
def ping():
    return "pong",200

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",5000)))