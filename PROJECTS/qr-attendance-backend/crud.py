import uuid
import qrcode
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import date, datetime
from models import Member, Attendance

def create_member(db, member_data):

    qr_id = f"QR_{uuid.uuid4().hex[:10]}"

    full_name = f"{member_data.first_name} {member_data.last_name}"

    db_member = Member(
        first_name=member_data.first_name,
        last_name=member_data.last_name,
        gender=member_data.gender,
        dob=member_data.dob,
        email=member_data.email,
        phone=member_data.phone,
        home_address=member_data.home_address,
        city=member_data.city,
        state=member_data.state,
        zip_code=member_data.zip_code,
        occupation=member_data.occupation,
        membership_type_preference=member_data.membership_type_preference,
        marital_status=member_data.marital_status,
        family_details=member_data.family_details,
        passport_photo_submitted=member_data.passport_photo_submitted,
        spiritual_information=member_data.spiritual_information,
        baptized=member_data.baptized,
        previously_part_of_church=member_data.previously_part_of_church,
        qr_id=qr_id
    )

    db.add(db_member)
    db.commit()
    db.refresh(db_member)

    # -----------------------
    # QR GENERATION SECTION
    # -----------------------

    # -----------------------
# QR GENERATION SECTION (Improved)
# -----------------------

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4
    )

    qr.add_data(qr_id)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    width, height = qr_img.size

    draw_font_size = 32

    try:
        font = ImageFont.truetype("arial.ttf", draw_font_size)
    except:
        font = ImageFont.load_default()

    full_name = f"{member_data.first_name} {member_data.last_name}"

    # Split long names into two lines if necessary
    words = full_name.split()

    if len(words) > 2:
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
    else:
        line1 = words[0]
        line2 = " ".join(words[1:]) if len(words) > 1 else ""

    text_height_space = 120

    new_img = Image.new("RGB", (width, height + text_height_space), "white")
    new_img.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(new_img)

    # Draw line 1
    bbox1 = draw.textbbox((0, 0), line1, font=font)
    text_width1 = bbox1[2] - bbox1[0]
    x1 = (width - text_width1) // 2
    y1 = height + 10

    draw.text((x1, y1), line1, fill="black", font=font)

    # Draw line 2
    if line2:
        bbox2 = draw.textbbox((0, 0), line2, font=font)
        text_width2 = bbox2[2] - bbox2[0]
        x2 = (width - text_width2) // 2
        y2 = y1 + 40

        draw.text((x2, y2), line2, fill="black", font=font)

    # Ensure QR folder exists
    if not os.path.exists("qr_codes"):
        os.makedirs("qr_codes")

    safe_first = member_data.first_name.replace(" ", "_")
    safe_last = member_data.last_name.replace(" ", "_")

    qr_path = f"qr_codes/{safe_first}_{safe_last}_{qr_id}.jpg"

    new_img.save(qr_path, "JPEG", quality=95)

    return db_member.member_id, qr_id, qr_path


def mark_attendance(db, qr_id, session_id):
    

    today = date.today()

    # 🔎 Find member by QR
    member = db.query(Member).filter(Member.qr_id == qr_id).first()

    if not member:
        return "not_found", None

    # 🔎 Check existing attendance
    existing = db.query(Attendance).filter_by(
        member_id=member.member_id,
        date=today,
        session_id=session_id
    ).first()

    if existing:
        return "already_marked", member

    # ✅ Create attendance record
    record = Attendance(
        member_id=member.member_id,
        date=today,
        time=datetime.now().time(),
        session_id=session_id
    )

    db.add(record)
    db.commit()

    return "marked", member

