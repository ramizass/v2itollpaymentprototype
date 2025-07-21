import os
import socket
import ssl
import time
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from RPLCD.i2c import CharLCD
from smbus2 import SMBus

SSID_TARGET = "What color is ur skyline?"
TCP_HOST, TCP_PORT = "10.36.166.78", 5000
BLOCK = 4
KEY_DEFAULT = [0xFF] * 6
TIDUR_CEK_SSID = 3

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=3)

def lcd_tulis(baris1="", baris2=""):
    lcd.clear()
    lcd.write_string(baris1[:16])
    if baris2:
        lcd.cursor_pos = (1, 0)
        lcd.write_string(baris2[:16])

def init_nfc():
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, irq=None, reset=None)
    pn532.SAM_configuration()
    return pn532

def baca_kartu(pn532):
    uid = pn532.read_passive_target(timeout=0.5)
    if not uid:
        return None

    if not pn532.mifare_classic_authenticate_block(uid, BLOCK, 0x60, KEY_DEFAULT):
        print("Autentikasi gagal!")
        return None

    data = pn532.mifare_classic_read_block(BLOCK)
    if not data:
        print("Gagal membaca data!")
        return None

    saldo = int.from_bytes(data[:2], "big")
    user_id = data[1:5]
    uid_str = "".join(f"{x:02X}" for x in uid)
    payload = f"UID: {uid_str}\nSaldo: {saldo}\nUser ID: {user_id.hex().upper()}\n"
    return uid, user_id, saldo, payload.encode()

def tulis_saldo(pn532, uid, user_id, saldo_baru):
    buf = saldo_baru.to_bytes(2, "big") + user_id + b"\x00" * (16 - 6)
    if pn532.mifare_classic_authenticate_block(uid, BLOCK, 0x60, KEY_DEFAULT):
        if pn532.mifare_classic_write_block(BLOCK, buf):
            print("Saldo di kartu diperbarui.")
        else:
            print("Gagal memperbarui saldo!")

def tersambung_ssid_target():
    return os.popen("iwgetid -r").read().strip() == SSID_TARGET

def kirim_ke_rsu(data, ctx):
    raw = socket.create_connection((TCP_HOST, TCP_PORT))
    with ctx.wrap_socket(raw, server_hostname=TCP_HOST) as ssock:
        t0 = time.time()
        ssock.sendall(data)
        resp = ssock.recv(1024)
        dt = time.time() - t0
    return resp, dt

def main():
    print(">>> OBU siap <<<")
    pn532 = init_nfc()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    transaksi_sudah_dilakukan = False

    lcd_tulis("Mencoba koneksi", "WiFi: RSU...")
    while not tersambung_ssid_target():
        print("Belum tersambung ke SSID target; menunggu…")
        time.sleep(TIDUR_CEK_SSID)

    print("Tersambung ke RSU. Siap NFC.")
    lcd_tulis("Tempelkan", "Kartu NFC")

    while True:
        if not tersambung_ssid_target():
            print("Terputus dari RSU. Mencoba koneksi kembali...")
            lcd_tulis("Mencoba koneksi", "WiFi: RSU...")
            while not tersambung_ssid_target():
                time.sleep(TIDUR_CEK_SSID)
            print("Tersambung kembali ke RSU.")
            lcd_tulis("Tempelkan", "Kartu NFC")
            transaksi_sudah_dilakukan = False  # reset flag

        hasil = baca_kartu(pn532)
        if hasil is None:
            time.sleep(0.5)
            continue

        if transaksi_sudah_dilakukan:
            print("Transaksi sudah dilakukan. Abaikan kartu.")
            lcd_tulis("Sudah Dibayar", "")
            time.sleep(0.5)
            continue

        uid, user_id, saldo_awal, data_bytes = hasil
        print("Data kartu terbaca. Kirim ke RSU…")

        retry = 0
        sukses = False

        while retry < 3 and not sukses:
            try:
                resp, delay = kirim_ke_rsu(data_bytes, ctx)
                resp_str = resp.decode().strip().upper()
                print(f"[RSU] balasan:\n{resp_str}")
                throughput = (len(data_bytes) + len(resp)) / delay if delay > 0 else 0
                print(f"[STAT] Delay {delay:.4f}s | Thput {throughput:.2f} B/s")

                if "GAGAL" in resp_str:
                    lcd_tulis("Pembayaran", "Gagal!")
                else:
                    if "SALDO:" in resp_str:
                        saldo_baru = int(resp_str.split("SALDO:")[1].strip())
                        tulis_saldo(pn532, uid, user_id, saldo_baru)
                    lcd_tulis("Pembayaran", "Berhasil!")
                    sukses = True
                    transaksi_sudah_dilakukan = True
                break
            except Exception as e:
                retry += 1
                print(f"Gagal kirim ({retry}/3):", e)
                time.sleep(1)

        if not sukses:
            lcd_tulis("Gagal Kirim", "Coba Lagi")
            print("Transaksi gagal total setelah 3 kali percobaan.")

        time.sleep(2)
        lcd_tulis("Tempelkan", "Kartu NFC")
        print("Transaksi selesai.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram dihentikan.")
        lcd.clear()