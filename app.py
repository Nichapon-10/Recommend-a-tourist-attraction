# -*- coding: utf-8 -*-
"""แอปแนะนำสถานที่ท่องเที่ยว (Streamlit + JSON)"""
import base64, json, os, shutil, html
from datetime import date
import pandas as pd
import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
UF, PF = os.path.join(DATA, "users.json"), os.path.join(DATA, "places.json")
SEED = os.path.join(DATA, "seed")
REGIONS = ["เหนือ", "กลาง", "อีสาน", "ตะวันออก", "ตะวันตก", "ใต้"]
CATS = ["ทะเล", "ภูเขา", "วัด", "น้ำตก", "เมือง", "คาเฟ่"]
NONE_NAME = "ไม่ระบุผู้แนะนำ"
PLACEHOLDER = "https://placehold.co/600x400/0EA5E9/FFF7ED?text=No+Image"

st.set_page_config(page_title="แนะนำสถานที่ท่องเที่ยว", page_icon="🌴", layout="wide")

# ---------- ข้อมูล ----------
def read_json(path):
    """อ่านไฟล์ JSON คืนเป็น list"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save():
    """เขียน users/places จาก session_state กลับไฟล์ JSON"""
    for path, key in ((UF, "users"), (PF, "places")):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(st.session_state[key], f, ensure_ascii=False, indent=2)

def ensure_seed():
    """สำรองข้อมูลตั้งต้นครั้งแรก เพื่อใช้กับปุ่ม Reset"""
    if not os.path.isdir(SEED):
        os.makedirs(SEED)
        shutil.copy(UF, os.path.join(SEED, "users.json"))
        shutil.copy(PF, os.path.join(SEED, "places.json"))

def load_state():
    """โหลดข้อมูลเข้า session_state ตอนเปิดแอป"""
    ensure_seed()
    if "users" not in st.session_state:
        st.session_state.users = read_json(UF)
        st.session_state.places = read_json(PF)

def reset_data():
    """คืนค่าข้อมูลตั้งต้น"""
    shutil.copy(os.path.join(SEED, "users.json"), UF)
    shutil.copy(os.path.join(SEED, "places.json"), PF)
    st.session_state.users = read_json(UF)
    st.session_state.places = read_json(PF)

def next_id(items):
    """สร้าง id ใหม่ (มากสุด + 1)"""
    return max([i["id"] for i in items], default=0) + 1

def uname(uid):
    """แปลง user id เป็นชื่อ"""
    for u in st.session_state.users:
        if u["id"] == uid:
            return u["name"]
    return NONE_NAME

def flash(msg):
    """เก็บข้อความสำเร็จไว้แสดงหลัง rerun"""
    st.session_state.flash = msg
    st.rerun()

def img_bytes_to_uri(file):
    """แปลงไฟล์ที่อัปโหลดเป็น data URI"""
    b64 = base64.b64encode(file.getvalue()).decode()
    return f"data:{file.type};base64,{b64}"

# ---------- ส่วนแสดงผล ----------
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stMarkdown, button, input, textarea {font-family:'Kanit',sans-serif !important;}
h1,h2,h3 {color:#0EA5E9;}
.hero {background:linear-gradient(120deg,#0EA5E9,#F97316);color:#fff;padding:2rem;border-radius:20px;margin-bottom:1rem;}
.hero h1 {color:#fff;margin:0;}
.card {background:#fff;border-radius:16px;box-shadow:0 4px 14px rgba(0,0,0,.12);overflow:hidden;margin-bottom:1rem;transition:transform .2s;}
.card:hover {transform:scale(1.03);}
.card img {width:100%;height:180px;object-fit:cover;display:block;}
.card .body {padding:.8rem 1rem;}
.badge {background:#F97316;color:#fff;border-radius:999px;padding:2px 10px;font-size:.8rem;}
.stars {color:#F59E0B;}
.avatar {width:64px;height:64px;border-radius:50%;object-fit:cover;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def img_tag(url, cls=""):
    """สร้าง <img> ที่ fallback เป็น placeholder ถ้าโหลดไม่ได้"""
    return f'<img class="{cls}" src="{html.escape(url or PLACEHOLDER)}" onerror="this.onerror=null;this.src=\'{PLACEHOLDER}\'">'

def stars(r):
    """แปลงเรตติ้งเป็นดาว"""
    n = int(round(r))
    return "★" * n + "☆" * (5 - n)

def card_html(p):
    """สร้าง HTML การ์ดสถานที่"""
    e = html.escape
    return f"""<div class="card">{img_tag(p['image'])}<div class="body">
<b>{e(p['name'])}</b> <span class="badge">{e(p['category'])}</span><br>
📍 {e(p['province'])} ({e(p['region'])})<br>
<span class="stars">{stars(p['rating'])}</span> {p['rating']:.1f}<br>
<small>🗓 {e(p['best_time'])} · 👤 {e(uname(p['user_id']))}</small><br>
<small>{e(p['description'])}</small></div></div>"""

def show_grid(places):
    """แสดงสถานที่เป็น grid 3 คอลัมน์"""
    if not places:
        st.info("ไม่พบสถานที่ที่ตรงเงื่อนไข")
        return
    for i in range(0, len(places), 3):
        cols = st.columns(3)
        for c, p in zip(cols, places[i:i + 3]):
            c.markdown(card_html(p), unsafe_allow_html=True)

# ---------- หน้า: หน้าแรก ----------
def page_home():
    """หน้าแรก"""
    st.markdown('<div class="hero"><h1>🌴 แนะนำสถานที่ท่องเที่ยวในไทย</h1>'
                '<p>แบ่งปันที่เที่ยวสุดประทับใจจากนักเดินทางทั่วประเทศ</p></div>', unsafe_allow_html=True)
    st.subheader("⭐ สถานที่เรตติ้งสูงสุด")
    top = sorted(st.session_state.places, key=lambda p: -p["rating"])[:3]
    show_grid(top)

# ---------- หน้า: สถานที่ ----------
def place_form(key, p=None):
    """ฟอร์มสถานที่ (ใช้ทั้งเพิ่มและแก้ไข) คืนค่า (submitted, data)"""
    p = p or {}
    users = st.session_state.users
    opts = [0] + [u["id"] for u in users]
    with st.form(key, clear_on_submit=(p == {})):
        name = st.text_input("ชื่อสถานที่", p.get("name", ""))
        c1, c2, c3 = st.columns(3)
        prov = c1.text_input("จังหวัด", p.get("province", ""))
        reg = c2.selectbox("ภาค", REGIONS, index=REGIONS.index(p["region"]) if p.get("region") in REGIONS else 0)
        cat = c3.selectbox("ประเภท", CATS, index=CATS.index(p["category"]) if p.get("category") in CATS else 0)
        url = st.text_input("URL รูปภาพ", p.get("image", ""))
        up = st.file_uploader("หรืออัปโหลดรูป (ถ้าเลือก จะใช้แทน URL)", type=["png", "jpg", "jpeg", "webp"])
        desc = st.text_area("คำบรรยาย", p.get("description", ""))
        c4, c5, c6 = st.columns(3)
        rating = c4.number_input("เรตติ้ง (1-5)", 0.0, 10.0, float(p.get("rating", 4.0)), 0.1)
        best = c5.text_input("ช่วงเวลาที่แนะนำ", p.get("best_time", ""))
        uid = c6.selectbox("ผู้แนะนำ", opts, format_func=lambda i: NONE_NAME if i == 0 else uname(i),
                           index=opts.index(p["user_id"]) if p.get("user_id") in opts else 0)
        ok = st.form_submit_button("💾 บันทึก")
    data = dict(name=name.strip(), province=prov.strip(), region=reg, category=cat,
                image=img_bytes_to_uri(up) if up else url.strip(), description=desc.strip(),
                rating=float(rating), best_time=best.strip(), user_id=uid or None)
    return ok, data

def valid_place(d):
    """ตรวจสอบข้อมูลสถานที่ คืนข้อความ error หรือ None"""
    if not d["name"]:
        return "ห้ามเว้นชื่อสถานที่ว่าง"
    if not 1 <= d["rating"] <= 5:
        return "เรตติ้งต้องอยู่ระหว่าง 1-5"
    return None

def page_places():
    """หน้าจัดการสถานที่"""
    st.header("🏝️ สถานที่ท่องเที่ยว")
    t1, t2, t3 = st.tabs(["🔎 ดูสถานที่", "➕ เพิ่ม", "✏️ แก้ไข / ลบ"])
    places = st.session_state.places
    with t1:
        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
        q = c1.text_input("ค้นหาชื่อสถานที่/จังหวัด")
        fr = c2.selectbox("ภาค", ["ทั้งหมด"] + REGIONS)
        fc = c3.selectbox("ประเภท", ["ทั้งหมด"] + CATS)
        mr = c4.slider("เรตติ้งขั้นต่ำ", 1.0, 5.0, 1.0, 0.1)
        so = c5.selectbox("เรียงตาม", ["เรตติ้งสูงสุด", "ชื่อ A-Z", "ใหม่สุด"])
        r = [p for p in places if (q.lower() in p["name"].lower() or q.lower() in p["province"].lower())
             and (fr == "ทั้งหมด" or p["region"] == fr) and (fc == "ทั้งหมด" or p["category"] == fc)
             and p["rating"] >= mr]
        r.sort(key={"เรตติ้งสูงสุด": lambda p: -p["rating"], "ชื่อ A-Z": lambda p: p["name"],
                    "ใหม่สุด": lambda p: -p["id"]}[so])
        st.caption(f"พบ {len(r)} แห่ง")
        show_grid(r)
    with t2:
        ok, d = place_form("add_place")
        if ok:
            err = valid_place(d)
            if err:
                st.error(err)
            else:
                d["id"] = next_id(places)
                places.append(d)
                save()
                flash(f"เพิ่มสถานที่ '{d['name']}' สำเร็จ")
    with t3:
        if not places:
            st.info("ยังไม่มีสถานที่")
            return
        pid = st.selectbox("เลือกสถานที่", [p["id"] for p in places],
                           format_func=lambda i: next(p["name"] for p in places if p["id"] == i))
        p = next(p for p in places if p["id"] == pid)
        ok, d = place_form(f"edit_place_{pid}", p)
        if ok:
            err = valid_place(d)
            if err:
                st.error(err)
            else:
                p.update(d)
                save()
                flash(f"แก้ไข '{d['name']}' สำเร็จ")
        st.divider()
        conf = st.checkbox("ยืนยันการลบสถานที่นี้", key=f"cp{pid}")
        if st.button("🗑️ ลบสถานที่", disabled=not conf, key=f"dp{pid}"):
            places.remove(p)
            save()
            flash(f"ลบ '{p['name']}' สำเร็จ")

# ---------- หน้า: ผู้ใช้ ----------
def valid_user(name, uid=None):
    """ตรวจสอบชื่อผู้ใช้ (ห้ามว่าง/ห้ามซ้ำ)"""
    name = name.strip()
    if not name:
        return "ห้ามเว้นชื่อว่าง"
    if any(u["name"].strip().lower() == name.lower() and u["id"] != uid for u in st.session_state.users):
        return "ชื่อผู้ใช้นี้ซ้ำแล้ว"
    return None

def page_users():
    """หน้าจัดการผู้ใช้"""
    st.header("👥 ผู้ใช้")
    users, places = st.session_state.users, st.session_state.places
    t1, t2, t3 = st.tabs(["📋 รายชื่อ", "➕ เพิ่ม", "✏️ แก้ไข / ลบ"])
    with t1:
        for u in users:
            c1, c2 = st.columns([1, 8])
            c1.markdown(img_tag(u["avatar"], "avatar"), unsafe_allow_html=True)
            n = sum(1 for p in places if p["user_id"] == u["id"])
            c2.markdown(f"**{u['name']}** · แนะนำ {n} แห่ง · สมัคร {u['joined']}  \n{u['bio']}")
    with t2:
        with st.form("add_user", clear_on_submit=True):
            name = st.text_input("ชื่อ")
            av = st.text_input("URL รูปโปรไฟล์")
            bio = st.text_area("bio สั้นๆ")
            ok = st.form_submit_button("💾 บันทึก")
        if ok:
            err = valid_user(name)
            if err:
                st.error(err)
            else:
                users.append(dict(id=next_id(users), name=name.strip(), avatar=av.strip(),
                                  bio=bio.strip(), joined=str(date.today())))
                save()
                flash(f"เพิ่มผู้ใช้ '{name.strip()}' สำเร็จ")
    with t3:
        if not users:
            st.info("ยังไม่มีผู้ใช้")
            return
        uid = st.selectbox("เลือกผู้ใช้", [u["id"] for u in users], format_func=uname)
        u = next(u for u in users if u["id"] == uid)
        with st.form(f"edit_user_{uid}"):
            name = st.text_input("ชื่อ", u["name"])
            av = st.text_input("URL รูปโปรไฟล์", u["avatar"])
            bio = st.text_area("bio", u["bio"])
            ok = st.form_submit_button("💾 บันทึกการแก้ไข")
        if ok:
            err = valid_user(name, uid)
            if err:
                st.error(err)
            else:
                u.update(name=name.strip(), avatar=av.strip(), bio=bio.strip())
                save()
                flash(f"แก้ไขผู้ใช้ '{name.strip()}' สำเร็จ")
        st.divider()
        owned = [p for p in places if p["user_id"] == uid]
        st.write(f"ผู้ใช้นี้แนะนำสถานที่ {len(owned)} แห่ง")
        mode = st.radio("เมื่อลบผู้ใช้ ให้จัดการสถานที่อย่างไร?",
                        [f"ย้ายไป '{NONE_NAME}'", "ลบสถานที่ของเขาด้วย"], key=f"m{uid}")
        conf = st.checkbox("ยืนยันการลบผู้ใช้นี้", key=f"cu{uid}")
        if st.button("🗑️ ลบผู้ใช้", disabled=not conf, key=f"du{uid}"):
            if mode.startswith("ลบ"):
                st.session_state.places = [p for p in places if p["user_id"] != uid]
            else:
                for p in owned:
                    p["user_id"] = None
            users.remove(u)
            save()
            flash(f"ลบผู้ใช้ '{u['name']}' สำเร็จ")

# ---------- หน้า: Dashboard ----------
def page_dashboard():
    """หน้าสรุปข้อมูล + Export + Reset"""
    st.header("📊 Dashboard")
    places, users = st.session_state.places, st.session_state.users
    avg = sum(p["rating"] for p in places) / len(places) if places else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("🏝️ สถานที่ทั้งหมด", len(places))
    c2.metric("👥 ผู้ใช้", len(users))
    c3.metric("⭐ เรตติ้งเฉลี่ย", f"{avg:.2f}")
    st.subheader("จำนวนสถานที่แยกตามภาค")
    cnt = pd.Series([p["region"] for p in places]).value_counts().reindex(REGIONS, fill_value=0)
    st.bar_chart(cnt, color="#0EA5E9")
    st.subheader("📥 Export ข้อมูล")
    dfp, dfu = pd.DataFrame(places), pd.DataFrame(users)
    a, b, c, d = st.columns(4)
    a.download_button("places.csv", dfp.to_csv(index=False).encode("utf-8-sig"), "places.csv", "text/csv")
    b.download_button("users.csv", dfu.to_csv(index=False).encode("utf-8-sig"), "users.csv", "text/csv")
    c.download_button("places.json", json.dumps(places, ensure_ascii=False, indent=2), "places.json")
    d.download_button("users.json", json.dumps(users, ensure_ascii=False, indent=2), "users.json")
    st.subheader("♻️ รีเซ็ตข้อมูล")
    conf = st.checkbox("ยืนยันการรีเซ็ตกลับข้อมูลตั้งต้น")
    if st.button("Reset", disabled=not conf):
        reset_data()
        flash("รีเซ็ตข้อมูลเรียบร้อย")

# ---------- main ----------
def main():
    """จุดเริ่มต้นของแอป"""
    load_state()
    if "flash" in st.session_state:
        msg = st.session_state.pop("flash")
        st.toast(msg, icon="✅")
        st.success(msg)
    st.sidebar.title("🧭 เมนู")
    page = st.sidebar.radio("ไปที่", ["🏠 หน้าแรก", "🏝️ สถานที่", "👥 ผู้ใช้", "📊 Dashboard"])
    {"🏠 หน้าแรก": page_home, "🏝️ สถานที่": page_places,
     "👥 ผู้ใช้": page_users, "📊 Dashboard": page_dashboard}[page]()

main()
