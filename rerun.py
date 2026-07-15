import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        print("🚀 Setting up ultra-efficient Kaggle Script Save Version trigger...")
        
        # 1. Verify and load repository secrets token blocks
        secret_auth_data = os.environ.get("KAGGLE_AUTH_JSON")
        if not secret_auth_data:
            print("❌ Error: Missing KAGGLE_AUTH_JSON environment variable secret!")
            sys.exit(1)
            
        with open("kaggle_auth.json", "w") as f:
            f.write(secret_auth_data)

        # Launching headless browser on desktop resolution
        browser = await p.chromium.launch(headless=True, args=["--window-size=1920,1080"])
        
        notebook_url = "https://kaggle.com/code/muhammadasjad2008/scheduler-2/edit"
        login_successful = False
        active_context = None
        active_page = None

        # ====================================================================
        # LAYER 1: PRIORITISE ROLLING CLOUD COOKIES (FUTURE AUTOMATION PATH)
        # ====================================================================
        if os.path.exists("state.json") and os.path.getsize("state.json") > 5:
            print("🔑 Path Selected: Attempting login with historical rolling state.json cloud cookies...")
            try:
                # FIXED: Corrected the viewport syntax from a comma-set to a structured key-value pair dictionary
                historical_context = await browser.new_context(
                    storage_state="state.json",
                    viewport={"width": 1920, "height": 1080}
                )
                historical_page = await historical_context.new_page()
                await historical_page.goto(notebook_url, wait_until="domcontentloaded", timeout=45000)
                
                # Verify if we successfully bypassed the login screen into the editor
                await historical_page.wait_for_selector("button:has-text('Save Version'), .edit-notebook", timeout=10000)
                print("✅ Success: Historical rolling cloud cookies verified! Session resumed.")
                
                active_context = historical_context
                active_page = historical_page
                login_successful = True
            except Exception as e:
                print(f"⚠️ Rolling cookies expired or not yet valid on this container branch: {e}")
                if 'historical_page' in locals(): await historical_page.close()
                if 'historical_context' in locals(): await historical_context.close()
                login_successful = False

        # ====================================================================
        # LAYER 2: FIRST-TIME RUN IMPORT (USES KAGGLE_AUTH_JSON SECRET ONLY ONCE)
        # ====================================================================
        if not login_successful:
            print("🔑 Path Selected: Bootstrapping session using KAGGLE_AUTH_JSON secret token layout...")
            try:
                original_context = await browser.new_context(
                    storage_state="kaggle_auth.json",
                    viewport={"width": 1920, "height": 1080}
                )
                original_page = await original_context.new_page()
                await original_page.goto(notebook_url, wait_until="domcontentloaded", timeout=90000)
                
                active_context = original_context
                active_page = original_page
                print("✅ Success: Initial login completed using repository token file framework.")
            except Exception as e:
                print(f"❌ Core navigation failed using backup token structures: {e}")
                sys.exit(1)

        # ====================================================================
            
        print("⏳ Waiting 30 seconds for the editor application layout to stabilize...")
        await active_page.wait_for_timeout(30000)

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
        
        opened_dialog = await active_page.evaluate(save_js)
        await active_page.wait_for_timeout(3000)

        if opened_dialog:
            print("🔘 'Save Version' menu opened. Confirming background run allocation...")
            try:
                confirm_btn = active_page.locator("button[data-test-id='save-version-dialog-save-button'], button:has-text('Save')").last
                await confirm_btn.click(timeout=10000)
                print("🚀 Background 'Save & Run All' successfully triggered!")
            except Exception as e:
                print(f"⚠️ Confirm button selector missed ({e}). Trying fallback keyboard confirm...")
                await active_page.keyboard.press("Enter")
        else:
            print("⚠️ Primary JS button locator missed. Deploying fallback hotkey sequence...")
            await active_page.focus("body")
            await active_page.keyboard.down("Control")
            await active_page.keyboard.down("Shift")
            await active_page.keyboard.press("s")
            await active_page.keyboard.up("Shift")
            await active_page.keyboard.up("Control")
            await active_page.wait_for_timeout(3000)
            await active_page.keyboard.press("Enter")
            print("⚡ Hotkey Save Version pipeline dispatched.")

        print("⏳ Waiting 15 seconds to ensure the backend server locks in the commit token...")
        await active_page.wait_for_timeout(15000)
        
        # ====================================================================
        # EXTRACTION STEP: EXPORT FRESH ACTIVE COOKIES BEFORE DISCONNECTING
        # ====================================================================
        try:
            print("💾 Extracting fresh session tokens from active page workspace configuration...")
            fresh_state = await active_context.storage_state()
            with open("state.json", "w") as sf:
                json.dump(fresh_state, sf, indent=2)
            print("🎉 Success: Refreshed token footprints written out cleanly to state.json.")
        except Exception as state_err:
            print(f"⚠️ Error dumping updated authentication state: {state_err}")
        
        print("\n" + "="*80)
        print("🎉 PIPELINE TRIGGER COMPLETE!")
        print("="*80 + "\n")
        
        # FIX STEP: Add a short 2-second sleep window to let loose execution loops close out cleanly
        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
