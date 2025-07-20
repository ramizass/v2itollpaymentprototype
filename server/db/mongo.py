from pymongo import MongoClient, DESCENDING  # tambahkan DESCENDING

def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["rsu_db"]
    return db

def get_transaksi():
    db = get_db()
    koleksi = db["transactions"]
    return list(koleksi.find().sort("_id", DESCENDING))  # urut berdasarkan _id terbaru duluan