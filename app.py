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


# -------------------- Entry Point --------------------

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # use PORT env (for Heroku/Cloud Run)
    app.run(host="0.0.0.0", port=port)
