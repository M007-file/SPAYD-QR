from flask import Flask, request, render_template, send_file
import os
import spayd

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    qr_file = None
    spayd_string = None
    form_data = {}
    QR_DIR = os.path.join(app.root_path, "static", "qr")
    os.makedirs(QR_DIR, exist_ok=True)

    if request.method == "POST":
        form_data = request.form.to_dict()
        # ---- defaulty pro FORMULÁŘ (ne pro QR!) ----
        form_data.setdefault("gradientColor1", "#ff0000")
        form_data.setdefault("gradientColor2", "#bd027c")
        form_data.setdefault("gradientType", "radial")
        form_data.setdefault("gradientOnEyes", "0")
        form_data.setdefault("useGradient", "0")
        form_data.setdefault("gradientOnEyes", "0")

        accountcountry   = form_data.get("country")
        accountbankcode  = form_data.get("bankcode")
        accountprefix    = form_data.get("prefix", "0")
        accountnumber    = form_data.get("number")
        amount           = form_data.get("amount")
        currency         = form_data.get("currency")
        varsymbol        = form_data.get("varsym")
        message          = form_data.get("messageforrecipient")
        recipientname    = form_data.get("recipient")

        # ===== IBAN =====
        iban = spayd.generate_iban(
            accountcountry,
            bank_code=accountbankcode,
            prefix=accountprefix,
            account=accountnumber,
        )

        # ===== SPAYD =====
        amount = "{:.2f}".format(float(amount.replace(",", ".")))
        spayd_string = f"SPD*1.0*ACC:{iban}*AM:{amount}*CC:{currency}"

        if varsymbol:
            spayd_string += f"*X-VS:{varsymbol}"
        if message:
            spayd_string += f"*MSG:{spayd.spayd_safe_text(message)}"
        if recipientname:
            spayd_string += f"*RN:{spayd.spayd_safe_text(recipientname)}"

        # ===== QR CONFIG =====
        spayd_config = {
            "body": form_data.get("qr_body", "mosaic"),
            "eye": form_data.get("qr_eye", "frame16"),
            "eyeBall": form_data.get("qr_eyeball", "ball19"),
            "bgColor": form_data.get("bgColor", "#FFFFFF"),
            "bodyColor": form_data.get("bodyColor", "#000000"),
            "colorLight": "#FFFFFF",
            "colorDark": "#000000",
            "errorCorrection": "H",
            "erf2": ["fh"],
            "erf3": ["fv"],
            "brf2": ["fh"],
            "brf3": ["fv"],
        }

        use_gradient = form_data.get("useGradient") == "1"

        if use_gradient:
            spayd_config["gradientType"] = form_data.get("gradientType", "radial")
            spayd_config["gradientColor1"] = form_data.get("gradientColor1")
            spayd_config["gradientColor2"] = form_data.get("gradientColor2")
            spayd_config["gradientOnEyes"] = form_data.get("gradientOnEyes") == "1"
        else:
            eye = form_data.get("eyeColor", "#000000")
            ball = form_data.get("eyeBallColor", "#000000")

            spayd_config.update({
                "eye1Color": eye,
                "eye2Color": eye,
                "eye3Color": eye,
                "eyeBall1Color": ball,
                "eyeBall2Color": ball,
                "eyeBall3Color": ball,
            })

        # ===== QR SIZE =====
        try:
            qr_size = int(form_data.get("qr_size", 600))
        except ValueError:
            qr_size = 600

        qr_size = max(200, min(qr_size, 2000))

        # ===== QR GENERATION =====
        qr_temp = os.path.join(QR_DIR, "qr_temp.png")
        final_qr = os.path.join(QR_DIR, "spayd_qr.png")
        prepared_logo = os.path.join(QR_DIR, "logo_prepared_temp.png")

        spayd.prepare_logo(os.path.join(QR_DIR, "petikoruna.jpg"), prepared_logo)
        spayd.generate_qr_monkey(spayd_string, spayd_config, qr_size, out_file=qr_temp)
        spayd.add_logo_to_qr(qr_temp, prepared_logo, final_qr)

        spayd.safe_remove(qr_temp)
        spayd.safe_remove(prepared_logo)

        qr_file = final_qr

    else:
        # ===== GET: pouze defaulty pro formulář =====
        form_data = {
            "country": "CZ",
            "bankcode": "6210",
            "prefix": "670100",
            "number": "2200921129",
            "amount": "1",
            "currency": "CZK",
            "varsym": "2025007",
            "recipient": "Jan Nováček",
            "messageforrecipient": "Platba",
            "qr_body": "square",
            "qr_eye": "frame0",
            "qr_eyeball": "ball0",
            "bodyColor": "#000000",
            "bgColor": "#ffffff",
            "eyeColor": "#000000",
            "eyeBallColor": "#000000",
            "qr_size": "600",
        }

    return render_template("qr-spayd.html", qr_file=qr_file, spayd_string=spayd_string, countries=spayd.IBAN_SCHEMAS.keys(), form_data=form_data, QR_BODY_SPRITES=spayd.QR_BODY_SPRITES, qr_eyes=spayd.QR_EYES, qr_eyeballs=spayd.QR_EYEBALLS, gradient_types=spayd.GRADIENT_TYPES)

# spusti server
if __name__ == "__main__":
    app.run(port=5000, debug=True)  #po jakekkoliv zmene se server sam resne a propisou se zmeny