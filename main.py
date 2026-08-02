import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup

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
        <title>Vidsrc Extractor Tester (ScraperAPI Edition)</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #1e1e1e; color: #fff; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: #2d2d2d; padding: 20px; border-radius: 8px; }
            input { padding: 10px; width: 70%; border: none; border-radius: 4px; outline: none; }
            button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            pre { background: #111; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; color: #00ff00; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Vidsrc JS Renderer Test</h2>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="tmdb_id" placeholder="TMDB ID Daalo (e.g., 969681)">
                <button onclick="fetchData()">Extract</button>
            </div>
            <h4 style="margin-top: 20px;">Response Data:</h4>
            <p style="font-size: 12px; color: #aaa;">Note: JS render hone mein 15-30 seconds lag sakte hain. Kripya wait karein...</p>
            <pre id="output">Waiting for request...</pre>
        </div>

        <script>
            async function fetchData() {
                const id = document.getElementById("tmdb_id").value;
                const output = document.getElementById("output");
                
                if(!id) {
                    output.innerText = "Please enter TMDB Code!";
                    return;
                }

                output.innerText = "ScraperAPI ke through render ho raha hai... Please wait (upto 30s).";

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
    
    # ScraperAPI ke parameters (render=true karna zaroori hai JS ke liye)
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': target_url,
        'render': 'true'
    }
    
    try:
        # Timeout 60 seconds diya hai kyunki browser load hone mein time lagta hai
        res = requests.get('http://api.scraperapi.com/', params=payload, timeout=60)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Rendered HTML se iframes nikal rahe hain
            iframes = [iframe.get('src') for iframe in soup.find_all('iframe') if iframe.get('src')]
            
            return {
                "status": "successed",
                "tmdb_id": tmdb_id,
                "found_iframes": iframes, 
                "message": "JS rendered successfully via ScraperAPI!"
            }
        else:
            return {
                "status": "failed", 
                "error": f"ScraperAPI returned HTTP {res.status_code}",
                "details": res.text
            }
            
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
