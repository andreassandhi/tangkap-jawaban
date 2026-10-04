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
    pilihan = {k: "" for k in KEYS}                  # soal 2 pilihan: Pilihan_C kosong
    pilihan.update(zip(KEYS, opsi))
    return pilihan, KEYS[opsi.index(benar)]


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


# =====================================================================
# USIA 3 TAHUN — lebih sederhana: 60% soal hanya 2 pilihan, angka 1-3,
# kunci 1 pasang, pola AB saja, kalimat lebih ramah.
# =====================================================================
def jumlah_opsi(i):
    return 2 if i % 5 < 3 else 3                    # 12 soal 2 pilihan, 8 soal 3 pilihan per kategori


def substitusi_3():
    out = []
    for i in range(20):
        nama_e, nama = rng.choice(BENDA)
        s = rng.sample(SIMBOL, 3)
        out.append(soal("Enkoding Substitusi", f"Lihat gambarnya! Kalau {nama}, jadi apa ya?",
                        f"{nama_e}➡️{s[0]} | {nama_e}➡️❓", s[0], s[1:jumlah_opsi(i)]))
    return out


WARNA_BENDA = [
    ("🍎", "apel", "🔴"), ("🍓", "stroberi", "🔴"), ("🍌", "pisang", "🟡"), ("🌻", "bunga matahari", "🟡"),
    ("🐸", "katak", "🟢"), ("🥦", "brokoli", "🟢"), ("🍊", "jeruk", "🟠"), ("🥕", "wortel", "🟠"),
    ("🍇", "anggur", "🟣"), ("🍆", "terong", "🟣"), ("🐳", "paus", "🔵"), ("💧", "air", "🔵"),
    ("🍫", "cokelat", "🟤"), ("🐘", "gajah", "⚪"),
]
BENTUK_SAMA = [("⭐", "bintang"), ("❤️", "hati"), ("🔺", "segitiga"), ("⚪", "lingkaran"), ("🟦", "kotak"), ("🌙", "bulan")]


def kombinasi_3():
    out = []
    benda = WARNA_BENDA[:]
    rng.shuffle(benda)
    semua_warna = sorted({w for _, _, w in WARNA_BENDA})
    for i in range(20):
        if i < 14:      # cocokkan warna benda
            e, nama, w = benda[i]
            salah = rng.sample([x for x in semua_warna if x != w], jumlah_opsi(i) - 1)
            out.append(soal("Enkoding Kombinasi", f"{nama.capitalize()} warnanya apa? Cari warna yang sama!",
                            f"{e} ➡️ 🎨❓", w, salah))
        else:           # cari bentuk yang sama
            e, nama = BENTUK_SAMA[i - 14]
            salah = rng.sample([x for x, _ in BENTUK_SAMA if x != e], jumlah_opsi(i) - 1)
            out.append(soal("Enkoding Kombinasi", f"Cari yang sama! Mana {nama}?", f"{e} ➡️ ❓", e, salah))
    rng.shuffle(out)
    return out


def enumerasi_3():
    out = []
    jumlah = ([1, 2, 3] * 7)[:20]
    rng.shuffle(jumlah)
    benda = rng.sample(BENDA, 20)
    label = lambda n: f"{n} " + "●" * n               # angka + titik bantu hitung
    for i, (n, (e, nama)) in enumerate(zip(jumlah, benda)):
        salah = rng.sample([x for x in (1, 2, 3) if x != n], jumlah_opsi(i) - 1)
        out.append(soal("Enumerasi Piktografik", f"Ayo hitung bersama! Ada berapa {nama}?",
                        " ".join([e] * n), label(n), [label(s) for s in salah]))
    return out


def kode_3():
    out = []
    for i in range(20):
        k = jumlah_opsi(i)                            # kunci 2 atau 3 angka
        benda = rng.sample(BENDA, k)
        kode = "   ".join(f"{KEYCAP[j + 1]}{b[0]}" for j, b in enumerate(benda))
        t = rng.randrange(k)
        out.append(soal("Substitusi Kode", f"Angka {ANGKA[t + 1]} itu gambar apa ya?",
                        f"{kode} | {KEYCAP[t + 1]}➡️❓", benda[t][0],
                        [b[0] for j, b in enumerate(benda) if j != t]))
    return out


def pola_3():
    out = []
    pools = [["🐱", "🐶", "🐰", "🐸"], ["🍎", "🍌", "🍇", "🍓"], ["🔴", "🔵", "🟡", "🟢"],
             ["⭐", "🌙", "☀️", "❤️"], ["🚗", "🎈", "⚽", "🌸"]]
    for i in range(20):
        a, b, c = rng.sample(pools[i % len(pools)], 3)
        seq = [a, b] * 3                              # a b a b a ?
        tampil, benar = seq[:5], seq[5]
        salah = [a] if jumlah_opsi(i) == 2 else [a, c]
        out.append(soal("Reproduksi Pola Sekuensial", "Lihat polanya! Habis ini apa ya?",
                        "".join(tampil) + "❓", benar, salah))
    return out


def susun(groups, usia):
    # Susun bergiliran antar kategori agar mode "berurutan" tetap bervariasi
    bank = [g[i] for i in range(20) for g in groups]
    for q in bank:
        q["usia"] = usia
        isi = [v for v in q["pilihan"].values() if v]
        assert len(set(isi)) == len(isi) >= 2, q
    return bank


def main():
    bank4 = susun([enkoding_substitusi(), enkoding_kombinasi(), enumerasi_piktografik(),
                   substitusi_kode(), reproduksi_pola()], "4")
    bank3 = susun([substitusi_3(), kombinasi_3(), enumerasi_3(), kode_3(), pola_3()], "3")
    bank = bank3 + bank4
    for i, q in enumerate(bank, 1):
        q["no"] = i

    # --- sisipkan ke index.html ---
    lines = []
    for q in bank:
        obj = {"no": q["no"], "usia": q["usia"], "kategori": q["kategori"], "soal": q["soal"], "gambar": q["gambar"],
               "pilihan": q["pilihan"], "kunci": q["kunci"]}
        js = json.dumps(obj, ensure_ascii=False)
        js = re.sub(r'"(no|usia|kategori|soal|gambar|pilihan|kunci|A|B|C)":', r"\1:", js)
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
    header = ["No", "Usia", "Kategori", "Soal", "Gambar", "Pilihan_A", "Pilihan_B", "Pilihan_C", "Kunci"]
    ws.append(header)
    for q in bank:
        p = q["pilihan"]
        ws.append([q["no"], int(q["usia"]), q["kategori"], q["soal"], q["gambar"], p["A"], p["B"], p["C"], q["kunci"]])
    fill = PatternFill("solid", fgColor="8B5CF6")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = fill
        c.alignment = Alignment(horizontal="center", vertical="center")
    for col, w in zip("ABCDEFGHI", [6, 7, 26, 48, 46, 14, 14, 14, 8]):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(vertical="center", wrap_text=True)
        for idx in (0, 1, 8):
            row[idx].alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "A2"
    dv = DataValidation(type="list", formula1='"A,B,C"', allow_blank=False,
                        error="Kunci harus A, B, atau C", errorTitle="Kunci tidak valid")
    ws.add_data_validation(dv)
    dv.add("I2:I2000")
    dv_usia = DataValidation(type="list", formula1='"3,4"', allow_blank=True,
                             error="Usia diisi 3 atau 4 (kosong = semua usia)", errorTitle="Usia tidak valid")
    ws.add_data_validation(dv_usia)
    dv_usia.add("B2:B2000")

    info = wb.create_sheet("Petunjuk")
    petunjuk = [
        ["PETUNJUK MENGISI SOAL — Tangkap Jawaban!"],
        [""],
        ["Kolom", "Wajib?", "Keterangan"],
        ["No", "Tidak", "Nomor urut (boleh dikosongkan, game akan menomori ulang)."],
        ["Usia", "Tidak", "Usia anak: 3 atau 4. Menu 'Usia anak' di game memilih soal sesuai usia ini. Kosong = tampil di semua usia."],
        ["Kategori", "Tidak", "Jenis permainan. Kategori baru otomatis muncul sebagai pilihan di menu. Kosong = 'Umum'."],
        ["Soal", "Ya", "Kalimat pendek. Teks ini ditampilkan DAN dibacakan oleh suara, jadi tulis dengan kata (bukan emoji)."],
        ["Gambar", "Tidak", "Emoji/simbol yang ditampilkan besar di bawah soal. Pakai tanda | untuk pindah baris. Contoh: 🍎➡️⭐  🍌➡️🔵 | 🍎➡️❓"],
        ["Pilihan_A / B", "Ya", "Pilihan jawaban. Boleh emoji (🍎), angka (3), atau kata pendek (Jakarta)."],
        ["Pilihan_C", "Tidak", "Pilihan ketiga. KOSONGKAN untuk soal 2 pilihan saja (cocok untuk usia 3 tahun)."],
        ["Kunci", "Ya", "Huruf jawaban yang benar: A, B, atau C (C hanya jika Pilihan_C diisi)."],
        [""],
        ["Cara import:", "", "Buka game → bagian 'Bank soal' → pilih 'Tambahkan' atau 'Ganti semua' → klik 📥 Import Soal → pilih file ini."],
        ["Catatan:", "", "Data diambil dari sheet bernama 'Soal' (atau sheet pertama). Baris kosong dilewati. File .csv (UTF-8) juga bisa."],
        ["", "", "Soal hasil import tersimpan di browser yang dipakai. Tombol '↩️ Pakai soal bawaan' mengembalikan 200 soal awal (100 usia 3 + 100 usia 4)."],
    ]
    for r in petunjuk:
        info.append(r)
    info["A1"].font = Font(bold=True, size=14, color="8B5CF6")
    for c in info[3]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = fill
    for r in (13, 14):
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
        key = f'{q["usia"]}th {q["kategori"]}'
        counts[key] = counts.get(key, 0) + 1
    print(f"{len(bank)} soal ->", counts)
    print("2 pilihan:", sum(not q["pilihan"]["C"] for q in bank))
    print("kunci:", {k: sum(q['kunci'] == k for q in bank) for k in KEYS})


if __name__ == "__main__":
    main()
