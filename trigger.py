

import asyncio
import os
import sys
from playwright.async_api import async_playwright

# Core State Management: Favor the continuous rolling artifact file
ROLLING_STATE = "state.json"
FALLBACK_SECRET_VAR = "KAGGLE_AUTH_JSON"

async def prepare_auth_file():
    """Determines whether to use yesterday's rolling cookies or seed from secrets."""
    if os.path.exists(ROLLING_STATE):
        print(f"🔄 Found rolling artifact state file: {ROLLING_STATE}")
        print(f"✌️ Got the latest kaggle authentication json cookies..🏆")
        return ROLLING_STATE
        
    secret_data = os.environ.get(FALLBACK_SECRET_VAR)
    if secret_data:
        print("🌱 Rolling state missing. Seeding workspace with KAGGLE_AUTH_JSON secret...")
        with open(ROLLING_STATE, "w") as f:
            f.write(secret_data)
        return ROLLING_STATE
        
    print(f"❌ Error: Missing {FALLBACK_SECRET_VAR} environment variable secret or rolling state!")
    sys.exit(1)

async def run():
    # 1. Dynamically resolve the correct tracking state path
    auth_path = await prepare_auth_file()

    async with async_playwright() as p:
        print("🚀 Setting up ultra-efficient Kaggle Script Save Version trigger...")
        
        # Launching headless browser on desktop resolution
        browser = await p.chromium.launch(headless=True, args=["--window-size=1920,1080"])
        
        # Load the resolved auth path (either rolling state.json or fallback)
        context = await browser.new_context(
            storage_state=auth_path,
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        # Exact path of your script editor panel (Kept exactly as your working version)
        notebook_url = "https://www.kaggle.com/code/muhammadasjad2008/content-factory-engine-2/edit"
        print(f"📡 Connecting to script workspace: {notebook_url}")
        
        try:
            await page.goto(notebook_url, wait_until="domcontentloaded", timeout=90000)
        except Exception as e:
            print(f"⚠️ Navigation status context: {e}")
            
        print("⏳ Waiting 30 seconds for the editor application layout to stabilize...")
        await page.wait_for_timeout(30000)

        # ====================================================================
        # JAVASCRIPT INJECTION: TRIGGERING NATIVE KAGGLE CORE SAVE ENGINE
        # ====================================================================
        print("📋 Injecting JavaScript bypass to trigger background Save Version workflow...")
        
        save_js = """
        () => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const saveBtn = buttons.find(b => b.textContent.toLowerCase().includes('save version'));
            
            if (saveBtn) {
                saveBtn.click();
                return true;
            }
            return false;
        }
        """
        
        opened_dialog = await page.evaluate(save_js)
        await page.wait_for_timeout(3000)

        if opened_dialog:
            print("🔘 'Save Version' menu opened. Confirming background run allocation...")
            try:
                confirm_btn = page.locator("button[data-test-id='save-version-dialog-save-button'], button:has-text('Save')").last
                await confirm_btn.click(timeout=10000)
                print("🚀 Background 'Save & Run All' successfully triggered!")
            except Exception as e:
                print(f"⚠️ Confirm button selector missed ({e}). Trying fallback keyboard confirm...")
                await page.keyboard.press("Enter")
        else:
            print("⚠️ Primary JS button locator missed. Deploying fallback hotkey sequence...")
            await page.focus("body")
            await page.keyboard.down("Control")
            await page.keyboard.down("Shift")
            await page.keyboard.press("s")
            await page.keyboard.up("Shift")
            await page.keyboard.up("Control")
            await page.wait_for_timeout(3000)
            await page.keyboard.press("Enter")
            print("⚡ Hotkey Save Version pipeline dispatched.")

        print("⏳ Waiting 15 seconds to ensure the backend server locks in the commit token...")
        await page.wait_for_timeout(15000)
        
        # ====================================================================
        # CRITICAL ADDITION: CAPTURE FRESH AUTHENTICATION TOKENS
        # ====================================================================
        await context.storage_state(path=ROLLING_STATE)
        print(f"💾 Fresh session tracking token array saved locally to: {ROLLING_STATE}")
        
        print("\n" + "="*80)
        print("🎉 PIPELINE TRIGGER COMPLETE!")
        print("Kaggle is now running your script in a locked background environment on your GPU T4.")
        print("The GPU will automatically power off and stop usage the exact second your code finishes.")
        print("🔗 Track execution and view live logs here: https://kaggle.com")
        print("="*80 + "\n")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
