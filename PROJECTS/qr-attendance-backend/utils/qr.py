import qrcode
import os

QR_DIR = "qrcodes"

def generate_qr(qr_id: str) -> str:
    # Ensure directory exists
    os.makedirs(QR_DIR, exist_ok=True)

    file_path = f"{QR_DIR}/{qr_id}.png"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(qr_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)

    return file_path
