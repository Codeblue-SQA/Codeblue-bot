"""
One-off sanity check: confirms the proxy is actually applied and that
the exit IP looks like a US address, before you trust it for real runs.

Usage:
    python verify_proxy.py
"""

from driver_factory import get_driver

CHECK_URL = "https://ipinfo.io/json"  # returns ip, city, region, country as JSON


def main():
    driver = get_driver(headless=True)
    driver.set_page_load_timeout(20)
    try:
        try:
            driver.get(CHECK_URL)
        except Exception as exc:
            print(f"[FAIL] Could not load {CHECK_URL} through the proxy within 20s.")
            print(f"Reason: {exc}")
            print("\nThis usually means the proxy IP is down/expired, not a code issue.")
            print("Try a different proxy from your provider's dashboard and update config.ini.")
            return

        body_text = driver.find_element("tag name", "body").text
        print("Proxy check response:")
        print(body_text)

        if '"country": "US"' in body_text or '"country":"US"' in body_text:
            print("\n[OK] Exit IP is US-based.")
        else:
            print("\n[WARNING] Exit IP does NOT look like US - check your proxy config/provider.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
