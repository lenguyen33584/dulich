from flask import Flask, request, send_file, after_this_request
from flask_cors import CORS
import subprocess
import os
import threading
import time

app = Flask(__name__)
CORS(app)

# Lock để đảm bảo chỉ 1 người được chạy bot tại 1 thời điểm
bot_lock = threading.Lock()

@app.route("/run-bot", methods=["POST"])
def run_bot():
    price = request.form.get("price", "no-price")
    print(f"💰 Nhận yêu cầu chạy bot với giá: {price}")

    # Thử chiếm lock — nếu đã có người đang chạy thì người sau phải đợi
    with bot_lock:
        print("🔒 Lock bot thành công — xử lý yêu cầu này...")
        start = time.time()

        # Gọi bot xử lý
        result = subprocess.run(["python3", "bot.py", price], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)

        # Đường dẫn ảnh QR đã cắt và ảnh toàn trang
        qr_image_path = os.path.join("static", "qr_code_detected.png")
        full_image_path = os.path.join("static", "full_page.png")

        if os.path.exists(qr_image_path):
            print(f"✅ Bot xử lý xong trong {int(time.time() - start)}s. Trả ảnh QR.")

            # ✅ Sau khi gửi file QR đã cắt, xóa cả 2 ảnh
            @after_this_request
            def remove_files(response):
                # Delay xoá nhẹ 2s để client tải về xong
                threading.Thread(target=delayed_delete, args=(qr_image_path, full_image_path)).start()
                return response

            return send_file(qr_image_path, mimetype="image/png")
        else:
            print("❌ Không tìm thấy ảnh QR sau khi chạy bot.")
            return "Không tìm thấy ảnh QR đã cắt!", 500

def delayed_delete(*paths):
    time.sleep(2)
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Đã xóa ảnh: {path}")
        except Exception as e:
            print(f"❌ Lỗi khi xóa ảnh {path}:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)