from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import sys, os
import cv2
sys.stdout.reconfigure(encoding='utf-8')
# ===================== NHẬN SỐ TIỀN =====================
if len(sys.argv) < 2:
    print("⚠️ Chưa truyền số tiền")
    sys.exit(1)

AMOUNT = sys.argv[1]
print("💰 Amount nhận được:", AMOUNT)

os.makedirs("static", exist_ok=True)

# ===================== CONFIG =====================
DEBUG_ADDR = "127.0.0.1:9222"
DEPOSIT_URL = "https://1xfun888bet.com/vi/office/recharge"
DEPOSIT_URL_KEYWORD = "recharge"
HOME_URL = "https://1xfun888bet.com/vi/office/recharge"

# ===================== ATTACH CHROME =====================
def attach_to_existing_chrome():
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUG_ADDR)
    return webdriver.Chrome(options=options)

# ===================== BYPASS SECURITY PAGE =====================
def bypass_security_warning(driver):
    try:
        title = driver.title.lower()
        print("📄 TITLE:", driver.title)

        if (
            "lỗi bảo mật" in title
            or "privacy error" in title
            or "security" in title
        ):
            print("⚠️ Security warning detected")

            driver.execute_script("""
                const btn = document.querySelector('#details-button');
                if (btn) btn.click();
            """)
            time.sleep(1)

            driver.execute_script("""
                const proceed = document.querySelector('#proceed-link');
                if (proceed) proceed.click();
            """)
            time.sleep(5)

            print("✅ Bypassed security warning")
            return True

    except Exception as e:
        print("bypass error:", e)

    return False

# ===================== CHỌN ĐÚNG TAB =====================
def switch_to_deposit_tab(driver):
    print("🔎 Đang tìm tab deposit...")

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        url = driver.current_url
        print("TAB:", url)

        if DEPOSIT_URL_KEYWORD in url:
            print("✅ Found deposit tab")
            bypass_security_warning(driver)
            return True

    print("⚠️ Không thấy tab deposit, mở mới...")
    driver.get(DEPOSIT_URL)
    time.sleep(5)
    bypass_security_warning(driver)
    return True

# ===================== CLICK MULTIPAY QR =====================
def select_multipay_qr(driver):
    time.sleep(5)

    # thử root trước
    try:
        result = driver.execute_script("""
            const el = document.querySelector("[data-rawmethod='multipay_qr_vn']");
            if (el) {
                el.scrollIntoView({block:'center'});
                el.click();
                return true;
            }
            return false;
        """)

        if result:
            print("✅ MultipayQR CLICKED (root)")
            return "root"
    except:
        pass

    # thử trong iframe
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"🧩 Found {len(iframes)} iframe(s)")

    for idx, iframe in enumerate(iframes):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(iframe)
            print(f"➡️ Switched to iframe {idx}")

            result = driver.execute_script("""
                const el = document.querySelector("[data-rawmethod='multipay_qr_vn']");
                if (el) {
                    el.scrollIntoView({block:'center'});
                    el.click();
                    return true;
                }
                return false;
            """)

            if result:
                print("✅ MultipayQR CLICKED (iframe)")
                return idx

        except Exception as e:
            print("iframe error:", e)

    print("❌ Không tìm thấy MultipayQR")
    return -1

# ===================== AUTO CHỌN BANK =====================
def auto_select_first_bank(driver):
    try:
        time.sleep(1)

        result = driver.execute_script("""
            const modal = document.querySelector("#payment_modal_container");
            if (!modal) return "NO_MODAL";

            const select = modal.querySelector("#bank_code");
            if (!select) return "NO_SELECT";

            const validOption = Array.from(select.options).find(
                o => o.value && o.value.trim() !== ""
            );

            if (!validOption) return "NO_OPTION";

            select.value = validOption.value;
            select.dispatchEvent(new Event("change", { bubbles: true }));

            const rendered = modal.querySelector("#select2-bank_code-container");
            if (rendered) {
                rendered.textContent = validOption.text;
                rendered.title = validOption.text;
            }

            return validOption.value + " | " + validOption.text;
        """)

        print("🏦 Bank result:", result)
        return result not in ["NO_MODAL", "NO_SELECT", "NO_OPTION"]

    except Exception as e:
        print("bank select error:", e)
        return False

# ===================== NHẬP TIỀN + CONFIRM =====================
def input_amount_and_confirm(driver, amount):
    time.sleep(2)

    auto_select_first_bank(driver)
    time.sleep(1)

    result = driver.execute_script(f"""
        const modal = document.querySelector("#payment_modal_container");
        if (!modal) return "NO_MODAL";

        const input = modal.querySelector("#amount");
        if (!input) return "NO_INPUT";

        input.focus();
        input.value = "";
        input.dispatchEvent(new Event("input", {{ bubbles: true }}));

        input.value = "{amount}";
        input.dispatchEvent(new Event("input", {{ bubbles: true }}));
        input.dispatchEvent(new Event("change", {{ bubbles: true }}));
        input.dispatchEvent(new Event("blur", {{ bubbles: true }}));

        return input.value;
    """)

    print("💵 Giá trị sau khi set:", result)

    time.sleep(1)

    clicked = driver.execute_script("""
        const modal = document.querySelector("#payment_modal_container");
        if (!modal) return false;

        const btn = modal.querySelector("#deposit_button");
        if (!btn) return false;

        btn.click();
        return true;
    """)

    if clicked:
        print("🚀 Đã click Confirm")
    else:
        print("❌ Không tìm thấy nút confirm")

# ===================== SCREENSHOT + CROP QR =====================
def screenshot_and_crop_qr(driver):
    detector = cv2.QRCodeDetector()
    full_img = "static/full_qr.png"
    out = "static/qr_only.png"

    print("⏳ Chờ QR render & detect")

    for i in range(1, 11):
        time.sleep(2)

        driver.save_screenshot(full_img)
        img = cv2.imread(full_img)

        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ok, pts = detector.detect(gray)

        print(f"🔎 Attempt {i} → detect={ok}")

        if ok and pts is not None:
            pts = pts[0].astype(int)

            x1, y1 = pts.min(axis=0)
            x2, y2 = pts.max(axis=0)

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(img.shape[1], x2)
            y2 = min(img.shape[0], y2)

            crop = img[y1:y2, x1:x2]
            cv2.imwrite(out, crop)

            print("🟢 QR OK → static/qr_only.png")
            print("📸 Full → static/full_qr.png")
            return True

    print("⚠️ Không detect QR – chỉ có full_qr.png")
    return False

# ===================== MAIN =====================
def main():
    driver = attach_to_existing_chrome()
    print("✅ Attached Chrome")

    if not switch_to_deposit_tab(driver):
        return

    print("📄 Current title:", driver.title)

    frame_result = select_multipay_qr(driver)

    if frame_result == -1:
        print(driver.page_source[:3000])
        return

    # nếu click trong iframe thì giữ nguyên iframe đó
    if frame_result == "root":
        driver.switch_to.default_content()

    input_amount_and_confirm(driver, AMOUNT)

    screenshot_and_crop_qr(driver)

    driver.get(HOME_URL)
    print("🏠 Đã load về trang chủ – bot vẫn sống")

# ===================== RUN =====================
if __name__ == "__main__":
    main()
