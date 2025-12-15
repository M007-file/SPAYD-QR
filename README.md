# SPAYD QR Generator (Flask)

This repository contains a web-based SPAYD QR code generator implemented in Python using Flask. The application generates valid SPAYD payment descriptors (SPD*1.0), computes IBANs according to official specifications, and produces customizable QR codes using the QRCodeMonkey API.

The project is intended as a technical demonstration and experimental tool for working with SPAYD payments, IBAN validation, and QR code customization. It is not intended for production or commercial use.

The application supports multiple countries (CZ, SK, DE, AT, PL), allows detailed customization of QR code appearance (body shape, eye style, colors, gradients), and optionally embeds a logo into the generated QR code. The web interface is implemented using Flask templates, CSS, and JavaScript, without any database or persistent storage.

This repository is provided **AS IS**, without any warranty of any kind, express or implied. The author assumes **no responsibility or liability** for errors, incorrect outputs, financial losses, or any damage resulting from the use or misuse of this software.

---

## Author

Developed and maintained by Michal Kopl.

- GitHub: https://github.com/M007-file
- LinkedIn: https://www.linkedin.com/in/michalkopl
- Blog: https://www.kopl.pro

## Purpose

This project was created as an exploration of the SPAYD payment standard,
IBAN generation, and QR code customization using a modern web interface.


## Project structure

```text
.
├── app.py                  # Flask web application
├── spayd.py                # Core SPAYD, IBAN, and QR logic
├── templates/
│   └── qr-spayd.html       # Main HTML template
├── static/
│   └── qr/
│       ├── qr-ui.css       # UI styles
│       ├── qr-ui.js        # UI and background logic
│       ├── qr-sprites.css  # QR sprite definitions
│       ├── spritesheet.png # QR shape sprites
│       └── petikoruna.jpg  # Example logo
└── README.md
```

---

## Usage

The application requires Python 3.9 or newer.

Required Python packages:
- Flask
- Requests
- Pillow

Install dependencies using pip and start the application by running:

```bash
python app.py
```

After starting the server, open a web browser and navigate to:

```
http://127.0.0.1:5000/
```

QR codes are generated using the public QRCodeMonkey API. Generated image files are stored temporarily in the `static/qr/` directory.

---

## License

See the `LICENSE.md` file for license information.
