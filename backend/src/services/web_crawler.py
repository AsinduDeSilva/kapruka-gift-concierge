import os
import sys
import json
import random
import asyncio
import threading
from loguru import logger
from playwright.async_api import async_playwright


class KaprukaWebCrawler:
    def __init__(self):
        self.base_url = "https://www.kapruka.com" 

    def get_product_category_urls(self):

        category_urls = []

        async def func():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(self.base_url, wait_until="domcontentloaded")

                await page.wait_for_selector('.rebrandCircles a', timeout=10000)

                a_tags = page.locator('.rebrandCircles a')
                count = await a_tags.count()

                for i in range(count):
                    href = await a_tags.nth(i).get_attribute('href')
                    if href and not href.endswith('.jsp'):
                        category_urls.append(href)

                await browser.close()

        self._run_in_thread(func)    

        return category_urls   

    def scrape_product_details(self, url):

        catalog = []

        async def func():
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ]
                )
                page = await browser.new_page()
                logger.info(f"Visiting: {url}")

                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                    await page.wait_for_selector("body", timeout=10000)
                    await page.wait_for_timeout(3000)  
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1000)
                    
                    for _ in range(17):
                        await page.wait_for_timeout(1500)
                        view_more_btn = page.locator('#pagination_btn')
                        if not await view_more_btn.is_visible():
                            break
                        await view_more_btn.scroll_into_view_if_needed()
                        await view_more_btn.click()

                    try:
                        await page.wait_for_selector('.catalogueV2Repeater a', timeout=15000)
                    except:
                        logger.warning("No products found")

                    products = page.locator('.catalogueV2Repeater a')
                    products_count = await products.count()
                    logger.info(f"Product count: {products_count}")

                    for i in range(products_count):
                        try:
                            href = await products.nth(i).get_attribute('href')
                            if not href:
                                continue

                            product_page = await browser.new_page()
                            await product_page.goto(href, wait_until="domcontentloaded")

                            #Cloudflare bypass
                            for j in range(2):
                                title = await product_page.title()
                                if "just a moment" in title.lower() or "cloudflare" in title.lower():
                                    logger.warning("Cloudflare challenge detected, waiting...")
                                    await product_page.wait_for_timeout(20000)

                                    if j == 1:
                                        logger.error("Cloudflare challenge not resolved")
                                        await product_page.close()
                                        continue    
                                else:
                                    if j == 1:
                                        logger.success("Cloudflare bypassed")
                                    break

                            
                            await product_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await product_page.wait_for_timeout(1000)

                            title = await product_page.locator('h1').first.inner_text()

                            price_locator = product_page.locator('#pricelbl')
                            if await price_locator.count() == 0:
                                logger.error(f"[{i+1}] Not a product page, skipping...")
                                await product_page.close()
                                continue
                            
                            discount_price_locator = product_page.locator('#priceAfterDiscountlbl')
                            if await discount_price_locator.count() > 0:
                                price = await discount_price_locator.inner_text()
                            else:
                                price = await price_locator.inner_text()

                            desc_locator = product_page.locator('.detailDescription')
                            description = await desc_locator.first.inner_text() if await desc_locator.count() else None

                            addtocartbutton = product_page.locator('#addtocartbutton')
                            availability = await addtocartbutton.count() > 0 
                                
                            product_data = {
                                'title': title,
                                'price': price,
                                'description': description,
                                'availability': availability,
                                'url': href
                            }

                            logger.success(f"[{i+1}] {product_data}")

                            catalog.append(product_data)

                            await product_page.close()

                            await asyncio.sleep(random.randint(1, 3))

                        except Exception as e:
                            logger.error(f"[{i+1}] Product error: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Category error: {e}")
                
                logger.success(f"Category {url} scraped successfully")
                await browser.close()
        
        self._run_in_thread(func) 

        return catalog

    def save_to_json(self, catalog, output_dir, filename = "catalog"):
        
        file_path = f"{output_dir}/{filename}.json"

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        data.extend(catalog)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.success(f"Catalog saved to {file_path}")

    def _run_in_thread(self, func):

        def worker():
            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(func())
            except Exception as e:
                print(e)
            finally:
                loop.close()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        thread.join()
