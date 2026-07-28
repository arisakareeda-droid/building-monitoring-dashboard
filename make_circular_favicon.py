"""
สคริปต์ครอปรูปโลโก้ให้เป็นวงกลมโปร่งใส สำหรับใช้เป็น favicon
วิธีใช้:
    1. วางไฟล์นี้ไว้โฟลเดอร์เดียวกับ logo.png
    2. รัน: python make_circular_favicon.py
    3. จะได้ไฟล์ใหม่ชื่อ logo_circular.png (มุมโปร่งใส ตรงกลางเป็นวงกลม)
    4. เอา logo_circular.png ไปตั้งเป็น favicon แทน logo.png เดิม
       (แก้ _LOGO_PATH ใน streamlit_app.py ให้ชี้ไปที่ logo_circular.png)
"""

from PIL import Image, ImageDraw, ImageOps

INPUT_PATH = "logo.png"
OUTPUT_PATH = "logo_circular.png"
SIZE = 256  # ขนาดที่ resize ก่อนครอป ยิ่งใหญ่ยิ่งคมชัด


def make_circular(input_path: str, output_path: str, size: int = 256):
    img = Image.open(input_path).convert("RGBA")

    # resize แบบ crop กลางภาพให้เป็นสี่เหลี่ยมจัตุรัสก่อน (กันภาพเบี้ยว)
    img = ImageOps.fit(img, (size, size), Image.LANCZOS, centering=(0.5, 0.5))

    # สร้าง mask วงกลม (ขาว = แสดง, ดำ = โปร่งใส)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    # ใส่ mask เป็น alpha channel
    img.putalpha(mask)

    img.save(output_path, "PNG")
    print(f"✅ สร้างไฟล์วงกลมสำเร็จ: {output_path}")


if __name__ == "__main__":
    make_circular(INPUT_PATH, OUTPUT_PATH, SIZE)
