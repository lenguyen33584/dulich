from flask import Flask, request, send_file, after_this_request
from flask_cors import CORS
import subprocess
import os
import threading
import time
import shutil
import uuid

app = Flask(__name__)
CORS(app)

# Lock để đảm bảo chỉ 1 người được chạy bot tại 1 thời điểm
bot_lock = threading.Lock()


@app.route("/run-bot", methods=["POST"])
def run_bot():
    price = request.form.get("price", "no-price")
    print(f"💰 Nhận yêu cầu chạy bot với giá: {price}")

    with bot_lock:
        print("🔒 Lock bot thành công — xử lý yêu cầu này...")
        start = time.time()

        # ===== RUN BOT =====
        try:
            result = subprocess.run(
                ["python", "bot3.py", price],
                capture_output=True,
                text=True,
                timeout=180
            )
        except subprocess.TimeoutExpired:
            print("⏰ Bot timeout!")
            return "Bot chạy quá lâu!", 500

        # ✅ LOG THỜI GIAN (FIX INDENT)
        elapsed = time.time() - start
        print(f"⏱️ BOT chạy mất: {elapsed:.2f} giây")

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        # ===== PATH CHUẨN =====
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        qr_image_path = os.path.join(BASE_DIR, "static", "qr_only.png")
        full_image_path = os.path.join(BASE_DIR, "static", "full_qr.png")

        print("📂 QR PATH:", qr_image_path)
        print("📂 FULL PATH:", full_image_path)

        # ===== CHECK BOT =====
        if result.returncode != 0:
            print(f"❌ Bot lỗi, returncode: {result.returncode}")

        # ===== CHECK FILE =====
        if os.path.exists(qr_image_path):
            print("✅ FILE QR TỒN TẠI")

            tmp_name = f"qr_{int(time.time())}_{uuid.uuid4().hex[:8]}.png"
            tmp_qr_path = os.path.join(BASE_DIR, "static", tmp_name)

            try:
                shutil.copyfile(qr_image_path, tmp_qr_path)
                print(f"🧷 COPY OK: {tmp_qr_path}")

                size = os.path.getsize(tmp_qr_path)
                print("📦 SIZE:", size)

                if size == 0:
                    print("❌ FILE RỖNG!")
                    return "QR rỗng!", 500

            except Exception as e:
                print("❌ COPY LỖI:", e)
                return "Lỗi copy QR!", 500

            # ===== DELETE SAU KHI GỬI =====
            @after_this_request
            def remove_files(response):
                threading.Thread(
                    target=delayed_delete,
                    args=(tmp_qr_path, qr_image_path, full_image_path),
                    daemon=True
                ).start()
                return response

            print("🚀 GỬI FILE VỀ CLIENT...")
            return send_file(tmp_qr_path, mimetype="image/png", as_attachment=False)

        else:
            print("❌ KHÔNG TÌM THẤY FILE QR")
            return "Không có QR!", 500


# ===== DELETE FILE =====
def delayed_delete(*paths):
    time.sleep(6)  # delay để client tải xong

    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Đã xóa: {path}")
        except Exception as e:
            print(f"❌ Lỗi xóa {path}:", e)


# ===== TEST API =====
@app.route("/test-image")
def test_image():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(BASE_DIR, "static", "qr_only.png")

    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return "No file", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
