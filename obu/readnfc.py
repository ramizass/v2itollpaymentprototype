import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C

# Setup I2C di Raspberry Pi
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, irq=None, reset=None)

# Konfigurasi PN532
pn532.SAM_configuration()

BLOCK = 4  # Blok tempat saldo & ID disimpan
KEY_DEFAULT = [0xFF] * 6  # Kunci default MIFARE Classic

print("Tempelkan kartu untuk membaca saldo & ID...")

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print(f"Kartu terdeteksi! UID: {''.join(format(x, '02X') for x in uid)}")

        # Authenticate sebelum membaca (Gunakan CMD_AUTH_A = 0x60)
        if pn532.mifare_classic_authenticate_block(uid, BLOCK, 0x60, KEY_DEFAULT):
            data_read = pn532.mifare_classic_read_block(BLOCK)

            if data_read:
                saldo = int.from_bytes(data_read[:2], "big")  # Mengambil 2 byte pertama
                user_id = data_read[1:5]

                print(f"Saldo: {saldo}")
                print(f"User ID: {''.join(format(x, '02X') for x in user_id)}")
            else:
                print("Gagal membaca data!")

        else:
            print("Autentikasi gagal!")

        time.sleep(2)