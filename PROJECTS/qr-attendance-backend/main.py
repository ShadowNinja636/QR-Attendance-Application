from fastapi.responses import FileResponse
import pandas as pd
from datetime import datetime
import os

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, crud

from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="QR Attendance Backend")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# Add Member
# ==========================
@app.post("/members/add")
def add_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):

    member_id, qr_id, qr_path = crud.create_member(db, member)

    return {
        "status": "success",
        "qr_id": qr_id,
        "member_id": member_id,
        "qr_image": qr_path,
        "message": "Member created successfully"
    }


# ==========================
# Scan Attendance (QR Based)
# ==========================
@app.post("/attendance/scan", response_model=schemas.ScanResponse)
def scan_attendance(req: schemas.ScanRequest, db: Session = Depends(get_db)):

    result, member = crud.mark_attendance(db, req.qr_id, req.session_id)

    

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Invalid QR code")

    full_name = f"{member.first_name} {member.last_name}"

    if result == "already_marked":
        return {
            "status": "warning",
            "message": "Attendance already marked",
            "name": full_name
        }

    return {
        "status": "success",
        "message": "Attendance recorded successfully",
        "name": full_name
    }



# ==========================
# Export Attendance to Excel
# ==========================
@app.get("/attendance/export")
def export_attendance(date: str, db: Session = Depends(get_db)):
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    records = (
        db.query(models.Attendance)
        .filter(models.Attendance.date == target_date)
        .all()
    )

    if not records:
        raise HTTPException(status_code=404, detail="No attendance records found")

    data = []

    for index, record in enumerate(records, start=1):
        member = db.query(models.Member).filter(
            models.Member.member_id == record.member_id
        ).first()

        data.append({
            "S.No": index,
            "First Name": member.first_name,
            "Last Name": member.last_name,
            "Gender": member.gender,
            "DOB": member.dob,
            "Email": member.email,
            "Phone": member.phone,
            "Home Address": member.home_address,
            "City": member.city,
            "State": member.state,
            "Zip Code": member.zip_code,
            "Occupation": member.occupation,
            "Membership Type Preference": member.membership_type_preference,
            "Marital Status": member.marital_status,
            "Family Details": member.family_details,
            "Passport Photo Submitted": member.passport_photo_submitted,
            "Spiritual Information": member.spiritual_information,
            "Baptized": member.baptized,
            "Previously Part Of Church": member.previously_part_of_church,
            "Attendance Time": record.time,
            "Attendance Date": record.date
        })

    df = pd.DataFrame(data)

    file_name = f"attendance_{date}.xlsx"
    df.to_excel(file_name, index=False)

    # ------------------------
    # Formatting Section
    # ------------------------

    wb = load_workbook(file_name)
    ws = wb.active

    # Make header bold + underlined
    for cell in ws[1]:
        cell.font = Font(bold=True, underline="single")

    # Auto-adjust column width
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)

        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass

        ws.column_dimensions[col_letter].width = max_length + 2

    wb.save(file_name)

    return FileResponse(
        path=file_name,
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.get("/qr/print-sheet")
def generate_qr_sheet(db: Session = Depends(get_db)):

    members = db.query(models.Member).all()

    if not members:
        raise HTTPException(status_code=404, detail="No members found")

    file_name = "qr_sheet.pdf"

    c = canvas.Canvas(file_name, pagesize=A4)

    page_width, page_height = A4

    x = 40
    y = page_height - 100

    qr_size = 120
    padding_x = 170
    padding_y = 180

    columns = 3
    col = 0

    for member in members:

        safe_first = member.first_name.replace(" ", "_")
        safe_last = member.last_name.replace(" ", "_")

        qr_path = f"qr_codes/{safe_first}_{safe_last}_{member.qr_id}.jpg"

        if not os.path.exists(qr_path):
            continue

        c.drawImage(qr_path, x, y, width=qr_size, height=qr_size)

        full_name = f"{member.first_name} {member.last_name}"

        c.setFont("Helvetica", 10)
        c.drawCentredString(x + qr_size/2, y - 10, full_name)

        x += padding_x
        col += 1

        if col >= columns:
            col = 0
            x = 40
            y -= padding_y

        if y < 100:
            c.showPage()
            x = 40
            y = page_height - 100

    c.save()

    return FileResponse(
        path=file_name,
        filename=file_name,
        media_type="application/pdf"
    )

@app.get("/attendance/count/today")
def get_today_attendance_count(db: Session = Depends(get_db)):
    from datetime import date

    today = date.today()

    count = db.query(models.Attendance).filter(
        models.Attendance.date == today
    ).count()

    return {"count": count}
