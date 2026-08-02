import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

# Tumhara ScraperAPI Key
SCRAPER_API_KEY = "660dc9f273c6860ca54be75cd9902b7a"

@app.get("/", response_class=HTMLResponse)
def serve_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vidsrc Deep Extractor (Enhanced)</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #1e1e1e; color: #fff; padding: 20px; }
            .container { max-width: 650px; margin: 0 auto; background: #2d2d2d; padding: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
            input { padding: 10px; width: 65%; border: none; border-radius: 4px; outline: none; background: #333; color: white; border: 1px solid #555; }
            button { padding: 10px 15px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #218838; }
            pre { background: #111; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; color: #00ff00; border: 1px solid #444; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Vidsrc Deep Extractor API</h2>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="tmdb_id" placeholder="Enter TMDB ID (e.g., 969680)">
                <button onclick="fetchData()">Start Extraction</button>
            </div>
            <h4 style="margin-top: 20px; color: #ffc107;">Response Data:</h4>
            <p style="font-size: 12px; color: #aaa;">Status: JS render ho raha hai... Isme 30 se 60 seconds lag sakte hain.</p>
            <pre id="output">Waiting for request...</pre>
        </div>

        <script>
            async function fetchData() {
                const id = document.getElementById("tmdb_id").value;
                const output = document.getElementById("output");
                
                if(!id) {
                    output.innerText = "Error: Please enter a valid TMDB ID!";
                    return;
                }

                output.innerText = "Scanning... Deep extraction in progress via ScraperAPI. Please wait...";

                try {
                    const response = await fetch(`/extract/${id}`);
                    const data = await response.json();
                    output.innerText = JSON.stringify(data, null, 4);
                } catch (error) {
                    output.innerText = "Error fetching data: " + error;
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/extract/{tmdb_id}")
def extract_vidsrc(tmdb_id: str):
    target_url = f"https://vidsrc.sbs/embed/movie/{tmdb_id}"
    
    # ScraperAPI Parameters (JS render on, aur original headers maintain rakhne ke liye)
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': target_url,
        'render': 'true',
        'keep_headers': 'true' # Yeh Vidsrc ko dikhayega ki hum direct wahi se aaye hain
    }
    
    try:
        # Timeout badha kar 60 seconds kar diya hai
        res = requests.get('http://api.scraperapi.com/', params=payload, timeout=60)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 1. Normal Iframes Scan
            iframes = [iframe.get('src') for iframe in soup.find_all('iframe') if iframe.get('src')]
            
            # 2. Deep Script Scan (Agar link JS ke andar chhipa ho)
            scripts = soup.find_all('script')
            hidden_urls = []
            for script in scripts:
                if script.string:
                    # Regex use karke scripts ke andar se URLs nikal rahe hain
                    urls = re.findall(r'(https?://[^\s"\',]+)', script.string)
                    for url in urls:
                        if 'vidsrc' in url or 'lizer' in url or 'embed' in url:
                            hidden_urls.append(url)
            
            return {
                "status": "success",
                "tmdb_id": tmdb_id,
                "message": "Enhanced Deep Scan completed via ScraperAPI!",
                "data_found": {
                    "direct_iframes": iframes,
                    "hidden_script_urls": list(set(hidden_urls)) # Duplicate links hata diye hain
                }
            }
        else:
            return {
                "status": "failed", 
                "error": f"ScraperAPI returned HTTP {res.status_code}",
                "details": res.text[:200]
            }
            
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
