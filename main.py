import uvicorn
from fastapi import FastAPI
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

@app.get("/extract/{tmdb_id}")
async def extract_vidsrc(tmdb_id: str):
    # Asli player ka URL construct kar rahe hain
    target_url = f"https://web.nxsha.app/embed/movie/{tmdb_id}?server=AwsPly-[Multi-Lang]"
    
    extracted_urls = {
        "m3u8_links": [],
        "ts_chunks": []
    }

    async with async_playwright() as p:
        # Headless browser launch karna
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            referer="https://vidsrc.sbs/"
        )
        page = await context.new_page()

        # Network requests ko hawa mein pakadne ka logic
        async def handle_request(request):
            url = request.url
            if ".m3u8" in url or "/getm3u8/" in url or "/stream/" in url:
                if url not in extracted_urls["m3u8_links"]:
                    extracted_urls["m3u8_links"].append(url)
            elif ".ts" in url or ".png" in url and "id=" in url:
                if url not in extracted_urls["ts_chunks"]:
                    extracted_urls["ts_chunks"].append(url)

        # Event listener lagana
        page.on("request", handle_request)

        try:
            # Player wale page par jana
            await page.goto(target_url, timeout=60000)
            
            # Page load hone ka thoda wait karna
            await asyncio.sleep(5)
            
            # Play button par click karne ki koshish karna (Deep scanning for play buttons)
            # Hum directly page par click inject kar rahe hain taaki agar fake button ho toh wo hat jaye
            await page.mouse.click(x=300, y=200) # Screen ke center-ish area mein click
            await asyncio.sleep(2)
            await page.mouse.click(x=300, y=200) # Double confirm click
            
            # Video play hone aur network tab mein link aane ka wait karna
            await asyncio.sleep(10)
            
        except Exception as e:
            return {"status": "error", "message": f"Execution error: {str(e)}"}
        finally:
            await browser.close()

    if len(extracted_urls["m3u8_links"]) > 0:
        return {
            "status": "success",
            "tmdb_id": tmdb_id,
            "message": "Play button clicked and network intercepted successfully!",
            "data": extracted_urls
        }
    else:
        return {
            "status": "failed",
            "message": "Click toh kiya, par network tab mein koi m3u8 link nahi mila. Protection strong ho sakti hai.",
            "data": extracted_urls
        }
