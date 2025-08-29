from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import qrcode
from PIL import Image
import io

app = Flask(__name__)
CORS(app)


def generate_qr(data, filename=None):
    """Generate a QR code and either save to file or return image object."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    if filename:
        img.save(filename)
        print(f"✅ QR Code saved as {filename}")
        img.show()
        return None
    return img


# -------------------- Flask Routes --------------------

@app.route("/")
def home():
    return jsonify({"message": "QR Code Generator API is running!"})


@app.route("/generate_qr", methods=["POST"])
def generate_qr_api():
    try:
        if request.is_json:
            data = request.json.get("data")
        else:
            data = request.form.get("data")

        if not data:
            return jsonify({"error": "No data provided"}), 400

        img = generate_qr(data)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return send_file(
            buf,
            mimetype="image/png",
            as_attachment=True,
            download_name="qrcode.png"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------- CLI Entry --------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Run as API server
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        # Run as CLI program
        user_input = input("Enter link or text for QR Code: ").strip()
        filename = input("Enter filename to save (default: qrcode.png): ").strip()

        if not filename:
            filename = "qrcode.png"
        elif not filename.lower().endswith(".png"):
            filename += ".png"

        generate_qr(user_input, filename)
