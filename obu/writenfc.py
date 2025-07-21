import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C

# Setup I2C untuk PN532
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, irq=None, reset=None)

# Konfigurasi PN532
pn532.SAM_configuration()

print("Tempelkan kartu RFID untuk menulis data...")

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print(f"Kartu terdeteksi! UID: {''.join(format(x, '02X') for x in uid)}")
        break

saldo = 50000  # Contoh saldo
saldo_bytes = list(saldo.to_bytes(2, "big"))  # Ubah ke byte (big-endian)

user_id = [0x12, 0x34, 0x56, 0x78]  # Contoh ID pengguna

# Blok data 16 byte (Saldo 2 byte + ID + padding)
data_to_write = saldo_bytes + user_id + [0] * 10


# Blok 4 untuk menyimpan data (MIFARE Classic)
BLOCK = 4

# Kunci default MIFARE Classic
KEY_DEFAULT = [0xFF] * 6

try:
    # Authenticate sebelum menulis (Gunakan CMD_AUTH_A = 0x60)
    if pn532.mifare_classic_authenticate_block(uid, BLOCK, 0x60, KEY_DEFAULT):
        print("Autentikasi sukses! Menulis data...")

        # Tulis data ke blok 4
        if pn532.mifare_classic_write_block(BLOCK, data_to_write):
            print("Data berhasil ditulis ke kartu!")
        else:
            print("Gagal menulis data.")

    else:
        print("Autentikasi gagal!")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")

time.sleep(2)