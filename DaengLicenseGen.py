import os
import json
import argparse
import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# --- Konfigurasi dasar ---
LICENSE_DIR = "licenses"
PRIVATE_KEY_PATH = "private.pem"

def load_private_key():
    """Membaca private.pem"""
    if not os.path.exists(PRIVATE_KEY_PATH):
        raise FileNotFoundError("File private.pem tidak ditemukan!")
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def sign_data(private_key, data_bytes):
    """Menandatangani data payload"""
    signature = private_key.sign(
        data_bytes,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature.hex()

def create_license(hwid, username, days_valid=365):
    """Membuat file lisensi JSON"""
    private_key = load_private_key()

    expiry_date = (datetime.datetime.utcnow() + datetime.timedelta(days=days_valid)).isoformat()

    payload = {
        "hwid": hwid,
        "user": username,
        "expiry": expiry_date
    }

    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    signature = sign_data(private_key, payload_bytes)

    license_data = {
        "payload": payload,
        "signature": signature
    }

    os.makedirs(LICENSE_DIR, exist_ok=True)
    license_path = os.path.join(LICENSE_DIR, f"license_{username}.json")

    with open(license_path, "w", encoding="utf-8") as f:
        json.dump(license_data, f, indent=4)

    print(f"[✅] License berhasil dibuat: {license_path}")
    print(f"[🔗] Upload ke GitHub lalu gunakan URL:")
    print(f"     https://raw.githubusercontent.com/DaengPatch11/Daengpatch.github.io.lisensi/main/{LICENSE_DIR}/license_{username}.json")

def main():
    parser = argparse.ArgumentParser(description="Daeng License Generator (Admin Tool)")
    parser.add_argument("--create", action="store_true", help="Buat lisensi baru")
    parser.add_argument("--hwid", type=str, help="HWID pengguna")
    parser.add_argument("--user", type=str, help="Nama pengguna")
    parser.add_argument("--days", type=int, default=365, help="Durasi aktif (hari)")
    args = parser.parse_args()

    if args.create:
        if not args.hwid or not args.user:
            print("[❌] Gunakan format:")
            print("    python DaengLicenseGen.py --create --hwid <HWID> --user <username> --days 365")
            return
        create_license(args.hwid, args.user, args.days)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
