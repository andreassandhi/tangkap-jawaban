"""Generate 100 soal bawaan untuk Tangkap Jawaban!

- Menyisipkan array SOAL_BAWAAN ke index.html (di antara penanda <SOAL_BAWAAN>)
- Membuat template_soal.xlsx (sheet "Soal" berisi 100 contoh + sheet "Petunjuk")

Jalankan:  python tools/generate_soal.py
"""
import json
import random
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
rng = random.Random(2026)
KEYS = ["A", "B", "C"]

BENDA = [
    ("🍎", "apel"), ("🍌", "pisang"), ("🍇", "anggur"), ("🍓", "stroberi"), ("🍊", "jeruk"),
    ("🐱", "kucing"), ("🐶", "anjing"), ("🐰", "kelinci"), ("🐟", "ikan"), ("🐘", "gajah"),
    ("🦆", "bebek"), ("🐸", "katak"), ("🐔", "ayam"), ("🚗", "mobil"), ("⚽", "bola"),
    ("🌸", "bunga"), ("🎈", "balon"), ("🍦", "es krim"), ("🦋", "kupu-kupu"), ("🐢", "kura-kura"),
]
SIMBOL = ["⭐", "❤️", "🔵", "🔺", "🟩", "🌙", "☀️", "🟣"]
ANGKA = {1: "satu", 2: "dua", 3: "tiga", 4: "empat", 5: "lima", 6: "enam"}
KEYCAP = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣"}

# warna -> (emoji per bentuk, benda contoh warna)
WARNA = {
    "merah": ({"lingkaran": "🔴", "kotak": "🟥", "hati": "❤️"}, "🍎"),
    "kuning": ({"lingkaran": "🟡", "kotak": "🟨", "hati": "💛"}, "🍌"),
    "hijau": ({"lingkaran": "🟢", "kotak": "🟩", "hati": "💚"}, "🐸"),
    "biru": ({"lingkaran": "🔵", "kotak": "🟦", "hati": "💙"}, "🐳"),
    "ungu": ({"lingkaran": "🟣", "kotak": "🟪", "hati": "💜"}, "🍇"),
    "oranye": ({"lingkaran": "🟠", "kotak": "🟧", "hati": "🧡"}, "🍊"),
}
BENTUK_PUTIH = {"lingkaran": "⚪", "kotak": "⬜", "hati": "🤍"}


def acak_pilihan(benar, salah):
    """Kembalikan (pilihan dict, kunci) dengan posisi jawaban benar diacak."""
    opsi = [benar] + list(salah)
    rng.shuffle(opsi)
    return dict(zip(KEYS, opsi)), KEYS[opsi.index(benar)]


def soal(kategori, teks, gambar, benar, salah):
    pilihan, kunci = acak_pilihan(benar, salah)
    return {"kategori": kategori, "soal": teks, "gambar": gambar, "pilihan": pilihan, "kunci": kunci}


def enkoding_substitusi():
    out = []
    for i in range(20):
        n = 2 if i < 12 else 3                     # 12 soal kunci 2 pasang, 8 soal kunci 3 pasang
        benda = rng.sample(BENDA, n)
        simbol = rng.sample(SIMBOL, n + 1)
        kunci_baris = "   ".join(f"{b[0]}➡️{s}" for b, s in zip(benda, simbol))
        t = rng.randrange(n)
        target, jawab = benda[t], simbol[t]
        lain = [s for j, s in enumerate(simbol[:n]) if j != t]
        salah = lain[:2] if n == 3 else lain + [simbol[n]]
        out.append(soal("Enkoding Substitusi", f"Lihat kuncinya! {target[1].capitalize()} jadi apa?",
                        f"{kunci_baris} | {target[0]}➡️❓", jawab, salah))
    return out


def enkoding_kombinasi():
    out = []
    warna = list(WARNA)
    bentuk = ["lingkaran", "kotak", "hati"]
    combos = [(w, b) for w in warna for b in bentuk]
    rng.shuffle(combos)
    combos += combos[:2]                           # 6 warna x 3 bentuk = 18, ulang 2 (pengecoh diacak lagi)
    for w, b in combos[:20]:
        emoji, contoh = WARNA[w]
        benar = emoji[b]
        bentuk_lain = rng.choice([x for x in bentuk if x != b])
        warna_lain = rng.choice([x for x in warna if x != w])
        salah = [emoji[bentuk_lain], WARNA[warna_lain][0][b]]   # warna sama bentuk beda, bentuk sama warna beda
        out.append(soal("Enkoding Kombinasi", f"Warna {w}, bentuk {b}. Mana {b} {w}?",
                        f"{contoh} ➕ {BENTUK_PUTIH[b]} ➡️ ❓", benar, salah))
    return out


def enumerasi_piktografik():
    out = []
    jumlah = [1, 2, 3, 4, 5] * 4
    rng.shuffle(jumlah)
    benda = rng.sample(BENDA, 20)
    for n, (e, nama) in zip(jumlah, benda):
        kandidat = [x for x in range(max(1, n - 2), min(6, n + 2) + 1) if x != n]
        salah = rng.sample(kandidat, 2)
        out.append(soal("Enumerasi Piktografik", f"Ayo hitung! Ada berapa {nama}?",
                        " ".join([e] * n), str(n), [str(s) for s in salah]))
    return out


def substitusi_kode():
    out = []
    for i in range(20):
        benda = rng.sample(BENDA, 3)
        kode = "   ".join(f"{KEYCAP[k + 1]}{b[0]}" for k, b in enumerate(benda))
        t = rng.randrange(3)
        if i % 2 == 0:   # angka -> gambar
            out.append(soal("Substitusi Kode", f"Lihat kodenya! Angka {ANGKA[t + 1]} itu gambar apa?",
                            f"{kode} | {KEYCAP[t + 1]}➡️❓", benda[t][0],
                            [b[0] for j, b in enumerate(benda) if j != t]))
        else:            # gambar -> angka
            out.append(soal("Substitusi Kode", f"Lihat kodenya! {benda[t][1].capitalize()} itu angka berapa?",
                            f"{kode} | {benda[t][0]}➡️❓", KEYCAP[t + 1],
                            [KEYCAP[j + 1] for j in range(3) if j != t]))
    return out


def reproduksi_pola():
    out = []
    pools = [
        ["🔴", "🔵", "🟡", "🟢", "🟣"], ["⭐", "🌙", "☀️", "❤️"], ["🍎", "🍌", "🍇", "🍓"],
        ["🐱", "🐶", "🐰", "🐸"], ["🚗", "⚽", "🎈", "🌸"],
    ]
    tipe = ["AB"] * 10 + ["AAB"] * 4 + ["ABB"] * 3 + ["ABC"] * 3
    for t in tipe:
        pool = rng.choice(pools)
        a, b, c, d = rng.sample(pool, 4)
        unit = {"AB": [a, b], "AAB": [a, a, b], "ABB": [a, b, b], "ABC": [a, b, c]}[t]
        panjang = {"AB": 5, "AAB": 5, "ABB": 5, "ABC": 5}[t] + rng.randrange(2)
        seq = [unit[k % len(unit)] for k in range(panjang + 1)]
        tampil, benar = seq[:-1], seq[-1]
        salah_pool = [x for x in dict.fromkeys(unit) if x != benar] + [d]
        salah = salah_pool[:2] if len(salah_pool) >= 2 else salah_pool + [c]
        out.append(soal("Reproduksi Pola Sekuensial", "Lihat polanya! Apa gambar selanjutnya?",
                        "".join(tampil) + "❓", benar, salah))
    return out


def main():
    groups = [enkoding_substitusi(), enkoding_kombinasi(), enumerasi_piktografik(),
              substitusi_kode(), reproduksi_pola()]
    # Susun bergiliran antar kategori agar mode "berurutan" tetap bervariasi
    bank = [g[i] for i in range(20) for g in groups]
    for i, q in enumerate(bank, 1):
        q["no"] = i
        assert len(set(q["pilihan"].values())) == 3, q

    # --- sisipkan ke index.html ---
    lines = []
    for q in bank:
        obj = {"no": q["no"], "kategori": q["kategori"], "soal": q["soal"], "gambar": q["gambar"],
               "pilihan": q["pilihan"], "kunci": q["kunci"]}
        js = json.dumps(obj, ensure_ascii=False)
        js = re.sub(r'"(no|kategori|soal|gambar|pilihan|kunci|A|B|C)":', r"\1:", js)
        lines.append("  " + js)
    block = "// <SOAL_BAWAAN>\nconst SOAL_BAWAAN = [\n" + ",\n".join(lines) + ",\n];\n// </SOAL_BAWAAN>"
    html_path = ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")
    html, n = re.subn(r"// <SOAL_BAWAAN>.*?// </SOAL_BAWAAN>", lambda _: block, html, flags=re.S)
    assert n == 1, "penanda SOAL_BAWAAN tidak ditemukan"
    html_path.write_text(html, encoding="utf-8")

    # --- template Excel ---
    wb = Workbook()
    ws = wb.active
    ws.title = "Soal"
    header = ["No", "Kategori", "Soal", "Gambar", "Pilihan_A", "Pilihan_B", "Pilihan_C", "Kunci"]
    ws.append(header)
    for q in bank:
        p = q["pilihan"]
        ws.append([q["no"], q["kategori"], q["soal"], q["gambar"], p["A"], p["B"], p["C"], q["kunci"]])
    fill = PatternFill("solid", fgColor="8B5CF6")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = fill
        c.alignment = Alignment(horizontal="center", vertical="center")
    for col, w in zip("ABCDEFGH", [6, 26, 48, 46, 14, 14, 14, 8]):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(vertical="center", wrap_text=True)
        row[0].alignment = row[7].alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "A2"
    dv = DataValidation(type="list", formula1='"A,B,C"', allow_blank=False,
                        error="Kunci harus A, B, atau C", errorTitle="Kunci tidak valid")
    ws.add_data_validation(dv)
    dv.add("H2:H2000")

    info = wb.create_sheet("Petunjuk")
    petunjuk = [
        ["PETUNJUK MENGISI SOAL — Tangkap Jawaban!"],
        [""],
        ["Kolom", "Wajib?", "Keterangan"],
        ["No", "Tidak", "Nomor urut (boleh dikosongkan, game akan menomori ulang)."],
        ["Kategori", "Tidak", "Jenis permainan. Kategori baru otomatis muncul sebagai pilihan di menu. Kosong = 'Umum'."],
        ["Soal", "Ya", "Kalimat pendek. Teks ini ditampilkan DAN dibacakan oleh suara, jadi tulis dengan kata (bukan emoji)."],
        ["Gambar", "Tidak", "Emoji/simbol yang ditampilkan besar di bawah soal. Pakai tanda | untuk pindah baris. Contoh: 🍎➡️⭐  🍌➡️🔵 | 🍎➡️❓"],
        ["Pilihan_A / B / C", "Ya", "Isi 3 pilihan jawaban. Boleh emoji (🍎), angka (3), atau kata pendek (Jakarta)."],
        ["Kunci", "Ya", "Huruf jawaban yang benar: A, B, atau C."],
        [""],
        ["Cara import:", "", "Buka game → bagian 'Bank soal' → pilih 'Tambahkan' atau 'Ganti semua' → klik 📥 Import Soal → pilih file ini."],
        ["Catatan:", "", "Data diambil dari sheet bernama 'Soal' (atau sheet pertama). Baris kosong dilewati. File .csv (UTF-8) juga bisa."],
        ["", "", "Soal hasil import tersimpan di browser yang dipakai. Tombol '↩️ Pakai soal bawaan' mengembalikan 100 soal awal."],
    ]
    for r in petunjuk:
        info.append(r)
    info["A1"].font = Font(bold=True, size=14, color="8B5CF6")
    for c in info[3]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = fill
    for r in (11, 12):
        info.cell(row=r, column=1).font = Font(bold=True)
    info.column_dimensions["A"].width = 20
    info.column_dimensions["B"].width = 9
    info.column_dimensions["C"].width = 100
    for row in info.iter_rows(min_row=3):
        for c in row:
            c.alignment = Alignment(vertical="top", wrap_text=True)

    wb.save(ROOT / "template_soal.xlsx")
    counts = {}
    for q in bank:
        counts[q["kategori"]] = counts.get(q["kategori"], 0) + 1
    print(f"{len(bank)} soal ->", counts)
    print("kunci:", {k: sum(q['kunci'] == k for q in bank) for k in KEYS})


if __name__ == "__main__":
    main()
