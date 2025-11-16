from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import cv2

# Thông tin đăng nhập
USERNAME = "lenguyen132"
PASSWORD = "nguoidung12345"

if len(sys.argv) < 2:
    print("khong co tien truyen vào")
    sys.exit(1)
AMOUNT = sys.argv[1]  # Lấy số tiền từ tham số dòng lệnh

# Tạo thư mục static nếu chưa có
if not os.path.exists("static"):
    os.makedirs("static")

# Khởi tạo trình duyệt Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Mở trình duyệt toàn màn hình
driver = webdriver.Chrome(options=options)

try:
    # Truy cập trang web
    driver.get("https://8xbet515.cc/deposit")
    wait = WebDriverWait(driver, 15)
    # Chờ trang load sau đăng nhập
    time.sleep(5)
    # Click vào nút mở form đăng nhập (có thể là "Login" hoặc "Đăng nhập")
    try:
        login_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-testid='submit-btn']")
        ))
        login_button.click()
        print("click vao nut dang nhap")
    except:
        print("khong tim thay nut dang nhap")

    # Nhập username
    try:
        user_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
        user_input.send_keys(USERNAME)
        print("nhap usename")
    except:
        print("khong tim thay o nhap usename")

    # Nhập password
    try:
        pass_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        pass_input.send_keys(PASSWORD)
        print("nhap password")
    except:
        print("khong tim thay o nhap password")

    # Click nút "Đăng Nhập"
    try:
        login_confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='submit-btn']")))
        login_confirm_button.click()
        print("dang nhap thanh cong")
    except:
        print("khong the click dang nhap")

    # Chờ trang load sau đăng nhập
    time.sleep(5)

    # Xử lý pop-up "Cancel" (hoặc tiếng Việt)
    try:
        cancel_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-testid='hint-popup-guide-primary-btn' and (text()='Cancel' or text()='Hủy')]")
        ))
        cancel_button.click()
        print("click huy")
    except:
        print("khong tim thay nut huy")

    # Xử lý pop-up "Later" (hoặc tiếng Việt)
    try:
        later_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='hint-popup-guide-primary-btn' and (text()='Later' or text()='Lần Sau')]")
        ))
        later_button.click()
        print("click vao later")
    except:
        print("khong tim thay nut later")

    # Click vào khoảng trống trên màn hình 2 lần để đóng hết pop-up
    try:
        empty_space = wait.until(EC.element_to_be_clickable((By.XPATH, "//body")))
        for i in range(2):
            empty_space.click()
            time.sleep(1)
            print(f"click vao khoang trong")
    except:
        print("khong the click vao khoang trong")

    # Click vào nút "Quét Mã QR Thanh Toán" (Tìm theo ảnh hoặc text)
    try:
        qr_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src, 'bankQRCode')]//ancestor::div[contains(@class, 'cursor-pointer')]")
        ))
        qr_button.click()
        print("click vào quet ma QR")

    except:
        print("khong tim thay nut QR")
        time.sleep(3)
        try:
            qr_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Quét Mã QR Thanh Toán') or contains(text(), 'Bank Direct Scan')]")
            ))
            qr_button.click()
            print("thu lai QR")
        except:
            print("bo qua buoc nay")

    # Chờ trang load
    time.sleep(3)

    # Nhập số tiền vào ô có `type="decimal"`
    try:
        amount_input = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='decimal']")
        ))
        amount_input.clear()
        amount_input.send_keys(AMOUNT)
        print(f"Nhập số tiền: {AMOUNT} VND")
    except:
        print("khong tim thay so tien nhap")

    # Click vào nút “Xác nhận nạp tiền”
    try:
        confirm_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-testid='deposit-third-party-submit-btn']")
        ))
        confirm_button.click()
        print("xac nhan nap tien")
    except:
        print("khong tim thay nut xac nhan nap tien")

    # Chờ pop-up hiện lên và click vào nút "Xác Nhận" để chuyển tới kênh thanh toán
    time.sleep(2)
    try:
        final_confirm_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-testid='friendly-tips-primary-btn']")
        ))
        final_confirm_button.click()
        print("click xac nhan de toi thanh toan")
    except:
        print("khong tim thay xac nhan")

    # Chờ tab mới mở ra và chuyển sang tab mới
    time.sleep(3)
    new_tab = driver.window_handles[-1]
    driver.switch_to.window(new_tab)
    print("da chuyen sang tab QR")

    # Chờ trang QR load xong
    time.sleep(5)

    # Bước 1: Chụp toàn bộ màn hình
    screenshot_path = "static/full_page.png"
    driver.save_screenshot(screenshot_path)
    print("da chup anh man hinh:", screenshot_path)

    # Bước 2: Phân tích ảnh và cắt vùng QR bằng OpenCV
    try:
        # Đọc ảnh
        img = cv2.imread(screenshot_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Phát hiện QR code
        detector = cv2.QRCodeDetector()
        retval, points = detector.detect(gray)

        if retval and points is not None:
            points = points[0].astype(int)
            x1, y1 = points.min(axis=0)
            x2, y2 = points.max(axis=0)

            qr_crop = img[y1:y2, x1:x2]
            qr_output_path = "static/qr_code_detected.png"
            cv2.imwrite(qr_output_path, qr_crop)
            print("Da cat QR va luu:", qr_output_path)
        else:
            print("khong tim thay QR trong anh chup")

    except Exception as e:
        print("Loi khi xu ly anh:", e)

except Exception as e:
    print(f"Loi xay ra: {e}")

finally:
    # Đóng trình duyệt
    driver.quit()