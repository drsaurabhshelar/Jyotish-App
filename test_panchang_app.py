import os
import time
from playwright.sync_api import sync_playwright

def run_test():
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to application
        page.goto("http://localhost:8000/panchang-v1.0.1.html")
        page.wait_for_load_state("networkidle")
        print("Loaded page successfully.")

        # Take initial screenshot
        page.screenshot(path=os.path.join(screenshots_dir, "01_initial_page.png"))

        # Select XML directory (passing directory path for webkitdirectory input)
        xml_dir = os.path.abspath("Kundalis")
        xml_input = page.locator("#xmlFolderInput")
        xml_input.set_input_files(xml_dir)
        print("Selected XML folder.")

        # Select Poster Template Image
        template_input = page.locator("#templateImageInput")
        template_input.set_input_files(os.path.abspath("template_poster.png"))
        print("Selected template poster image.")

        time.sleep(1)

        # Take screenshot with records loaded and preview rendered
        page.screenshot(path=os.path.join(screenshots_dir, "02_loaded_files_preview.png"))

        # Verify table records
        records_count = page.locator("#recordsTableBody tr").count()
        print(f"Table records count: {records_count}")
        assert records_count == 3, f"Expected 3 records, got {records_count}"

        # Click submit button to generate wishes and expect download
        submit_btn = page.locator("#submitBtn")
        with page.expect_download(timeout=15000) as download_info:
            submit_btn.click()
            print("Clicked submit button.")

        download = download_info.value
        zip_path = os.path.join(screenshots_dir, download.suggested_filename)
        download.save_as(zip_path)
        print(f"Successfully downloaded 8K wishes archive: {zip_path}")

        time.sleep(1)
        # Final screenshot after complete generation
        page.screenshot(path=os.path.join(screenshots_dir, "03_generation_complete.png"))

        browser.close()
        print("Test completed successfully!")

if __name__ == "__main__":
    run_test()
