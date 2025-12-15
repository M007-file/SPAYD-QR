# SPAYD-QR
FLASK - Python application to generate a customizable payment QR code

# SPAYD QR Generator

A web-based SPAYD (Short Payment Descriptor) QR code generator built with Python and Flask.

The project generates **valid SPAYD payment strings** in accordance with the official specification and renders customizable QR codes via the QRCodeMonkey API.  
It supports advanced visual configuration (QR body, eyes, colors, gradients) and optional logo embedding.

The implementation is intended primarily for **development, experimentation, and self-hosted use**.

---

## Features

- Valid SPAYD string generation
- IBAN generation with checksum validation
- Support for multiple countries (CZ, SK, DE, AT, PL)
- SPAYD-compliant text sanitization
- Customizable QR design:
  - QR body shapes
  - Eye and eyeball styles
  - Solid colors or gradients
- Optional gradient application to QR eyes
- Logo embedding into the QR code
- Web UI built with Flask and vanilla HTML/CSS/JS
- No external frontend frameworks

---

## Project Structure

.
├── app.py # Flask web application
├── spayd.py # Core SPAYD, IBAN, and QR logic
├── templates/
│ └── qr-spayd.html # Main HTML template
├── static/
│ └── qr/
│ ├── qr-ui.css # UI styles
│ ├── qr-ui.js # UI and background logic
│ ├── qr-sprites.css # QR sprite definitions
│ ├── spritesheet.png # QR shape sprites
│ └── petikoruna.jpg # Example logo
└── README.md


Temporary files and cache directories are intentionally excluded from version control.

## Requirements

- Python 3.9+
- pip packages:
  - Flask
  - requests
  - Pillow

Install dependencies:
pip install flask requests pillow

Running the Application
python app.py

The development server will start on:
http://localhost:5000

The app runs in debug mode by default and reloads automatically on code changes.

SPAYD Specification
The SPAYD format follows the official specification:
https://qr-platba.cz/pro-vyvojare/

All user-provided text fields are sanitized to comply with the allowed SPAYD character set (uppercase ASCII, no diacritics).

QR Code Generation
QR codes are generated via the QRCodeMonkey API:
https://www.qrcode-monkey.com/qr-code-api-with-logo/

This project does not implement its own QR rendering engine.

Notes and Limitations
This project depends on a third-party API for QR rendering.

No authentication, rate limiting, or persistence is implemented.
Intended for local use, demos, or internal tools.

Not designed as a payment gateway or production payment processor.

## Disclaimer

This repository is provided **"AS IS"**, without any express or implied warranty.  
The authors make no guarantees regarding correctness, reliability, or fitness for any particular purpose.

Use of this software is entirely at your own risk.  
The authors assume no responsibility or liability for errors, omissions, data loss, financial loss, or any other damages resulting from the use or misuse of this project.
