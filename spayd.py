import requests
import os
import unicodedata
from PIL import Image   # pip install pillow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_QR_DIR = os.path.join(BASE_DIR, "static", "qr")
os.makedirs(STATIC_QR_DIR, exist_ok=True)

# ===============================================================
# skript pro generování VALIDNIHO SPAYD QR kódu
# inspirován službou https://www.qrcode-monkey.com/
#
# SPAYD specifikace:
# https://qr-platba.cz/pro-vyvojare/
# ===============================================================

# ======================= KONFIGURACE UCTU ======================
# ISO 3166-1 alpha-2
ACCOUNT_COUNTRY = "CZ"

# vse MUSI byt stringy
bankprefix = "670100"      # CZ: prefix, jinde je ignorovano
bankaccount = "2200921129"
bankcode = "6210"
# ===============================================================

# ======================= SPAYD PARAMETRY =======================
am = "1"
cc = "CZK"
vs = "2025007"

msg = "Jenom zkouška generátoru"
rn = "Pepa z Depa"
# ===============================================================

# ================= konfigurace QR vzhledu ======================
QR_BODY_SPRITES = {
    "square": 0,
    "mosaic": 1,
    "dot": 2,
    "circle": 3,
    "circle-zebra": 4,
    "circle-zebra-vertical": 5,
    "circular": 6,
    "edge-cut": 7,
    "edge-cut-smooth": 8,
    "japanese": 9,
    "leaf": 10,
    "pointed": 11,
    "pointed-edge-cut": 12,
    "pointed-in": 13,
    "pointed-in-smooth": 14,
    "pointed-smooth": 15,
    "round": 16,
    "rounded-in": 17,
    "rounded-in-smooth": 18,
    "rounded-pointed": 19,
    "star": 20,
    "diamond": 21,
}

def build_qr_config(form):
    cfg = {
        "body": form.get("qr_body", "mosaic"),
        "eye": form.get("qr_eye", "frame16"),
        "eyeBall": form.get("qr_eyeball", "ball19"),
        "bgColor": form.get("bgColor", "#FFFFFF"),
        "bodyColor": form.get("bodyColor", "#000000"),
        "colorLight": "#FFFFFF",
        "colorDark": "#000000",
        "errorCorrection": "H",
        "erf2": ["fh"],
        "erf3": ["fv"],
        "brf2": ["fh"],
        "brf3": ["fv"],
    }

    if form.get("useGradient") == "1":
        cfg["gradientType"] = form.get("gradientType", "radial")
        cfg["gradientColor1"] = form.get("gradientColor1", "#FF0000")
        cfg["gradientColor2"] = form.get("gradientColor2", "#BD027C")
        cfg["gradientOnEyes"] = form.get("gradientOnEyes") == "1"
    else:
        eye = form.get("eyeColor", "#000000")
        ball = form.get("eyeBallColor", "#000000")
        cfg.update({
            "eye1Color": eye,
            "eye2Color": eye,
            "eye3Color": eye,
            "eyeBall1Color": ball,
            "eyeBall2Color": ball,
            "eyeBall3Color": ball,
        })

    return cfg


QR_BODIES = [
    "square", "mosaic", "dot", "round", "star", "circle",
    "circle-zebra", "circle-zebra-vertical", "circular",
    "edge-cut", "edge-cut-smooth", "japnese", "leaf",
    "pointed", "pointed-edge-cut", "pointed-in",
    "pointed-in-smooth", "pointed-smooth",
    "rounded-in", "rounded-in-smooth",
    "rounded-pointed", "diamond",
]

QR_EYES = [
    "frame0","frame1","frame2","frame3","frame4","frame5",
    "frame6","frame7","frame8","frame9","frame10","frame11",
    "frame12","frame13","frame14","frame15",
]

QR_EYEBALLS = [
    "ball0","ball1","ball2","ball3","ball5","ball6","ball7",
    "ball8","ball10","ball11","ball12","ball13","ball14",
    "ball15","ball16","ball17","ball18","ball19",
]

GRADIENT_TYPES = ["linear", "radial"]
# ================= konfigurace QR vzhledu ======================

# ===================== SPAYD TEXT SANITIZER ====================
# dle SPAYD povolene znakove sady (uppercase ASCII, bez diakritiky)
def spayd_safe_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.upper()

    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 +-./()"
    text = "".join(ch if ch in allowed else " " for ch in text)

    return " ".join(text.split())


msg = spayd_safe_text(msg)
rn = spayd_safe_text(rn)

# ===================== IBAN GENERATOR ==========================
# ISO 3166-1 alpha-2 (kody zemi)
# ISO 13616 (IBAN)
# ISO/IEC 7064 (MOD 97-10)

IBAN_SCHEMAS = {
    # ===========================================================
    # CZ – Česká republika
    # IBAN délka: 24
    # Struktura:
    # CZ kk BBBB PPPPPP AAAAAAAAAA
    #  2  2   4    6        10     = 24
    #
    # BBBB     = kód banky
    # PPPPPP   = prefix účtu (pokud není, tak 000000)
    # AAAAAAAAAA = číslo účtu
    #
    # Příklad:
    # CZ65 0800 000019 2000145399
    # ===========================================================
    "CZ": {
        "length": 24,
        "bban": [
            ("bank_code", 4),
            ("prefix", 6),
            ("account", 10),
        ],
    },

    # ===========================================================
    # SK – Slovensko
    # IBAN délka: 24
    # Struktura:
    # SK kk BBBB AAAAAAAAAAAAAAAA
    #  2  2   4         16       = 24
    #
    # Slovensko NEMA prefix účtu
    #
    # Příklad:
    # SK31 1100 0000000029387437
    # ===========================================================
    "SK": {
        "length": 24,
        "bban": [
            ("bank_code", 4),
            ("account", 16),
        ],
    },

    # ===========================================================
    # DE – Německo
    # IBAN délka: 22
    # Struktura:
    # DE kk BBBBBBBB AAAAAAAAAA
    #  2  2    8          10    = 22
    #
    # BBBBBBBB  = BLZ (kód banky)
    # AAAAAAAAAA = číslo účtu
    #
    # Příklad:
    # DE89 3704 0044 0532 0130 00
    # ===========================================================
    "DE": {
        "length": 22,
        "bban": [
            ("bank_code", 8),
            ("account", 10),
        ],
    },

    # ===========================================================
    # AT – Rakousko
    # IBAN délka: 20
    # Struktura:
    # AT kk BBBBB AAAAAAAAAAA
    #  2  2   5        11    = 20
    #
    # Příklad:
    # AT61 1904 3002 3457 3201
    # ===========================================================
    "AT": {
        "length": 20,
        "bban": [
            ("bank_code", 5),
            ("account", 11),
        ],
    },

    # ===========================================================
    # PL – Polsko
    # IBAN délka: 28
    # Struktura:
    # PL kk BBBBBBBB AAAAAAAAAAAAAAAA
    #  2  2    8            16       = 28
    #
    # Délka 28 je daná dlouhým domácím číslem účtu
    #
    # Příklad:
    # PL61 1090 1014 0000 0712 1981 2874
    # ===========================================================
    "PL": {
        "length": 28,
        "bban": [
            ("bank_code", 8),
            ("account", 16),
        ],
    },
}


def _iban_checksum(country_code: str, bban: str) -> str:
    rearranged = bban + country_code + "00"
    numeric = ""

    for ch in rearranged:
        if ch.isalpha():
            numeric += str(ord(ch) - 55)
        else:
            numeric += ch

    return f"{98 - (int(numeric) % 97):02d}"

def generate_iban(country_code: str, **parts) -> str:
    country_code = country_code.upper()

    if country_code not in IBAN_SCHEMAS:
        raise ValueError(f"Nepodporovana zeme: {country_code}")

    schema = IBAN_SCHEMAS[country_code]
    bban = ""

    for field, length in schema["bban"]:
        value = str(parts.get(field, "")).zfill(length)

        if len(value) != length or not value.isdigit():
            raise ValueError(
                f"{field} musi mit delku {length} cislic pro zemi {country_code}"
            )

        bban += value

    checksum = _iban_checksum(country_code, bban)
    iban = f"{country_code}{checksum}{bban}"

    if len(iban) != schema["length"]:
        raise ValueError("Neplatna delka IBAN")

    return iban

# ====================== DESIGN LOGA ============================
def prepare_logo(logo_src, logo_out, target_color=(0, 0, 0)):
    logo_src = os.path.join(BASE_DIR, logo_src)
    logo_out = os.path.join(BASE_DIR, logo_out)

    img = Image.open(logo_src).convert("RGBA")
    data = img.getdata()

    new_data = []
    for r, g, b, *a in data:
        if r > 200 and g > 200 and b > 200:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append((*target_color, 255))

    img.putdata(new_data)
    img.save(logo_out, "PNG")
    return logo_out

# ====================== QR MONKEY API ==========================
# Dokumentace:
# https://www.qrcode-monkey.com/qr-code-api-with-logo/
def generate_qr_monkey(data_text, config, size_px=1000, fmt="png", out_file="qr_temp.png"):
    out_file = os.path.join(BASE_DIR, out_file)
    url = "https://api.qrcode-monkey.com/qr/custom"

    body = {
        "data": data_text,
        "config": config,
        "size": size_px,
        "download": True,
        "file": fmt.lower(),
    }

    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)

    if resp.status_code != 200:
        raise RuntimeError("Chyba API QRCodeMonkey: " + str(resp.status_code))

    content_type = resp.headers.get("Content-Type", "").lower()

    if content_type.startswith("image/"):
        with open(out_file, "wb") as f:
            f.write(resp.content)
        return out_file

    result = resp.json()
    image_url = result.get("imageUrl") or result.get("image")

    if not image_url:
        raise RuntimeError("QR API nevratilo imageUrl")

    if image_url.startswith("//"):
        image_url = "https:" + image_url

    img = requests.get(image_url).content
    with open(out_file, "wb") as f:
        f.write(img)

    return out_file

# ====================== LOGO DO QR =============================
def add_logo_to_qr(qr_path, logo_path, out_path, scale=0.25):
    qr = Image.open(os.path.join(BASE_DIR, qr_path)).convert("RGBA")
    logo = Image.open(os.path.join(BASE_DIR, logo_path)).convert("RGBA")

    w, h = qr.size
    logo_size = int(min(w, h) * scale)
    logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

    pos = ((w - logo.width) // 2, (h - logo.height) // 2)

    qr.alpha_composite(logo, dest=pos)
    qr.convert("RGB").save(os.path.join(BASE_DIR, out_path), "PNG")

    return out_path

# ====================== MAZANI TEMP SOUBORU ====================
def safe_remove(path):
    full = os.path.join(BASE_DIR, path)
    if os.path.exists(full):
        os.remove(full)

# ====================== HLAVNI BEH =============================
if __name__ == "__main__":

    acciban = generate_iban(
        ACCOUNT_COUNTRY,
        bank_code=bankcode,
        prefix=bankprefix,
        account=bankaccount,
    )

    am = "{:.2f}".format(float(am.replace(",", ".")))

    spayd_data = f"SPD*1.0*ACC:{acciban}*AM:{am}*CC:{cc}*X-VS:{vs}*MSG:{msg}*RN:{rn}"

    print("SPAYD:", spayd_data)

    spayd_config = {
        "body": "mosaic",
        "eye": "frame16",
        "eyeBall": "ball19",
        "bgColor": "#FFFFFF",
        "colorLight": "#FFFFFF",
        "bodyColor": "#000000",
        "colorDark": "#000000",
        "eye1Color": "#000000",
        "eye2Color": "#000000",
        "eye3Color": "#000000",
        "gradientOnEyes": True,
        "errorCorrection": "H",
        "gradientType": "radial",
        "gradientColor1": "#FF0000",
        "gradientColor2": "#BD027C",
        "erf2": ["fh"],
        "erf3": ["fv"],
        "brf2": ["fh"],
        "brf3": ["fv"],
    }

    input_logo    = os.path.join(STATIC_QR_DIR, "petikoruna.png")
    prepared_logo = os.path.join(STATIC_QR_DIR, "logo_prepared_temp.png")
    qr_temp       = os.path.join(STATIC_QR_DIR, "qr_temp.png")
    final_qr      = os.path.join(STATIC_QR_DIR, "spayd_qr.png")

    prepare_logo(input_logo, prepared_logo)
    generate_qr_monkey(spayd_data, spayd_config, size_px=1200, out_file=qr_temp)
    add_logo_to_qr(qr_temp, prepared_logo, final_qr)

    safe_remove(qr_temp)
    safe_remove(prepared_logo)

    print("Hotovo:", os.path.join(BASE_DIR, final_qr))
