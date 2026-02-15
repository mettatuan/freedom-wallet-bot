"""
Generate OCB Bank QR Code for donations
"""
import qrcode
from pathlib import Path

# OCB Bank Transfer Info
BANK_INFO = {
    "bank": "OCB",
    "account": "0814267626",
    "account_name": "PHAM THANH TUAN",
    "amount": "",  # Optional
    "description": "FW Donation"
}

# VietQR format for OCB
# Format: bank_id|account_number|account_name|amount|description|template
# OCB bank code: 970201
qr_data = f"970201|{BANK_INFO['account']}|{BANK_INFO['account_name']}||{BANK_INFO['description']}|compact2"

# Generate QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(qr_data)
qr.make(fit=True)

# Create image
img = qr.make_image(fill_color="black", back_color="white")

# Save to media folder
media_path = Path(__file__).parent.parent / "media" / "images"
media_path.mkdir(parents=True, exist_ok=True)

output_file = media_path / "donation_qr_ocb.png"
img.save(output_file)

print(f"✅ QR Code generated: {output_file}")
print(f"📱 Bank: OCB")
print(f"💳 Account: {BANK_INFO['account']}")
print(f"👤 Name: {BANK_INFO['account_name']}")
