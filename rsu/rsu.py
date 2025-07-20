import socket
import ssl
import time
from pymongo import MongoClient

HOST = "0.0.0.0"
PORT = 5000
CERT_PATH = "/home/robbyan/server.crt"
KEY_PATH = "/home/robbyan/server.key"
TOLL_FEE = 3000
EXPIRE_CACHE = 2  # detik

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['rsu_db']
collection = db['transactions']

# ────────────────────────────────────────────────────────────────
# Utilitas
# ────────────────────────────────────────────────────────────────

uid_cache = {}

def parse_line(raw, key):
    for line in raw.splitlines():
        if key in line:
            return line.split(":")[1].strip()
    return None

def hitung_stat(data_len, start, end):
    delay = end - start
    thrpt = data_len / delay if delay > 0 else 0
    return delay, thrpt

# ────────────────────────────────────────────────────────────────
# Proses 1 klien
# ────────────────────────────────────────────────────────────────

def proses_klien(conn, addr):
    print(f"[RSU] Koneksi dari {addr}")
    try:
        start = time.time()
        data = conn.recv(1024)
        recv_time = time.time()
        decoded = data.decode()
        print("[DATA DITERIMA]\n", decoded)

        delay, throughput = hitung_stat(len(data), start, recv_time)
        print(f"[INFO] Delay: {delay:.4f}s | Throughput: {throughput:.2f} B/s")

        uid = parse_line(decoded, "UID")
        user_id = parse_line(decoded, "User ID")
        saldo = int(parse_line(decoded, "Saldo") or 0)
        now = time.time()
        status = ""
        saldo_baru = saldo  # default sama

        if uid:
            # Cek duplikat UID
            if uid in uid_cache:
                selisih = now - uid_cache[uid]
                if selisih < EXPIRE_CACHE:
                    print(f"[SKIP] UID {uid} duplikat dalam {selisih:.2f}s")
                    status = "duplikat"
                    conn.sendall(f"SKIPPED\nSaldo: {saldo}".encode())
                    simpan(uid, user_id, saldo, saldo, delay, throughput, status)
                    return

            # Cache UID
            uid_cache[uid] = now

            # Proses transaksi
            if saldo >= TOLL_FEE:
                saldo_baru = saldo - TOLL_FEE
                status = "berhasil"
                response = f"UPDATE\nSaldo: {saldo_baru}"
            else:
                status = "gagal"
                response = f"GAGAL\nSaldo: {saldo_baru}"

            conn.sendall(response.encode())
            print("[RESPON TERKIRIM]\n", response)

            # Simpan ke DB
            simpan(uid, user_id, saldo, saldo_baru, delay, throughput, status)

    except Exception as e:
        print("[ERROR]", e)
    finally:
        conn.close()
        print(f"[RSU] Koneksi {addr} ditutup.\n")

# ────────────────────────────────────────────────────────────────
# Menyimpan data di database
# ────────────────────────────────────────────────────────────────

def simpan(uid, user_id, saldo_awal, saldo_akhir, delay, throughput, status):
    doc = {
        "uid": uid,
        "user_id": user_id,
        "saldo_awal": saldo_awal,
        "saldo_akhir": saldo_akhir,
        "delay": round(delay, 6),
        "throughput": round(throughput, 2),
        "status": status,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    collection.insert_one(doc)
    print("[DB] Data disimpan ke MongoDB")

# ────────────────────────────────────────────────────────────────
# Entry-point server
# ────────────────────────────────────────────────────────────────

def jalankan_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_PATH, KEY_PATH)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(5)
        print(f"[RSU] Listening di port {PORT}…\n")

        while True:
            raw_sock, addr = srv.accept()
            with context.wrap_socket(raw_sock, server_side=True) as ssl_sock:
                proses_klien(ssl_sock, addr)

if _name_ == "_main_":
    jalankan_server()