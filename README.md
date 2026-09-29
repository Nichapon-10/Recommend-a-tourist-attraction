# 🌴 แนะนำสถานที่ท่องเที่ยว (Streamlit)

เว็บแอป CRUD ผู้ใช้ + สถานที่ท่องเที่ยว เก็บข้อมูลเป็นไฟล์ JSON

## ติดตั้งและรัน
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy ขึ้น GitHub + Streamlit Community Cloud
1. `git init && git add . && git commit -m "first commit"`
2. สร้าง repo บน GitHub แล้ว `git remote add origin <URL> && git push -u origin main`
3. เข้า https://share.streamlit.io → New app → เลือก repo, branch `main`, ไฟล์ `app.py` → Deploy

## หมายเหตุสำคัญ
- บน Streamlit Cloud ไฟล์ที่แก้ไขขณะรันจะ **รีเซ็ตกลับเป็นข้อมูลตั้งต้นเมื่อ reboot/redeploy**
- ต้องการเก็บข้อมูลถาวร ให้ใช้ปุ่ม Export หรือเปลี่ยนไปใช้ฐานข้อมูลภายนอก
- รูปภาพเริ่มต้นเป็น URL จาก Unsplash หากรูปไหนโหลดไม่ขึ้น แอปจะแสดงรูป placeholder อัตโนมัติ
- รูปที่อัปโหลดจะถูกแปลงเป็น base64 เก็บใน JSON
