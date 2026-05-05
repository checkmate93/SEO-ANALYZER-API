from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import textstat
from bs4 import BeautifulSoup
import requests
import re
from collections import Counter
import math
import uvicorn

app = FastAPI(
    title="Ultimate SEO & Readability Analyzer API",
    description="Analyzes text and URLs for SEO keywords, readability scores, and vocabulary entropy.",
    version="1.0.0"
)

# montelo
class TextPayload(BaseModel):
    text: str

class UrlPayload(BaseModel):
    url: str

# h analush
def analyze_content(text: str):
    if not text or len(text) < 10:
        raise HTTPException(status_code=400, detail="Text too short for meaningful analysis.")
    
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    words = clean_text.split()
    
    readability_score = textstat.flesch_reading_ease(text)
    grade_level = textstat.text_standard(text)
    reading_time = round(len(words) / 200, 2)
    
    stop_words = {'the', 'a', 'to', 'of', 'and', 'in', 'is', 'it', 'you', 'that', 'he', 'was', 'for', 'on', 'are', 'with', 'as', 'I', 'his', 'they', 'be', 'at', 'one', 'have', 'this', 'from', 'or', 'had', 'by', 'not', 'but', 'what', 'some', 'we', 'can', 'out', 'other', 'were', 'all', 'there', 'when', 'up', 'use', 'your', 'how', 'said', 'an', 'each', 'she'}
    meaningful_words = [w for w in words if w not in stop_words and len(w) > 3]
    keywords = Counter(meaningful_words).most_common(10)
    
    # Shannon Entropy
    total = len(meaningful_words)
    entropy = 0.0
    if total > 0:
        counts = Counter(meaningful_words).values()
        for count in counts:
            p = count / total
            entropy -= p * math.log2(p)

    return {
        "metrics": {
            "word_count": len(words),
            "character_count": len(text),
            "estimated_reading_time_minutes": reading_time,
        },
        "readability": {
            "flesch_reading_ease": round(readability_score, 1),
            "grade_level": grade_level,
            "status": "Easy to read" if readability_score > 60 else "Moderate" if readability_score > 40 else "Difficult to read"
        },
        "seo_analysis": {
            "top_keywords": [{"keyword": k[0], "density_percent": round((k[1]/len(words))*100, 2)} for k in keywords],
            "vocabulary_entropy_score": round(entropy, 2)
        }
    }

# to frontend mou
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SEO Analyzer API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                background: #fafafa;
                margin: 0;
                padding: 20px;
                color: #3b3b3b;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            }
            h1 {
                font-size: 24px;
                font-weight: 600;
                margin: 0 0 8px 0;
                color: #2c3e50;
            }
            .subtitle {
                color: #6c757d;
                font-size: 14px;
                margin-bottom: 30px;
            }
            .input-group {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            input[type="url"], textarea {
                flex: 1;
                padding: 10px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                font-family: inherit;
            }
            input:focus, textarea:focus {
                outline: none;
                border-color: #4a90e2;
            }
            button {
                background: #3b82c4;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 4px;
                font-size: 14px;
                cursor: pointer;
                font-weight: 500;
            }
            button:hover {
                background: #2563eb;
            }
            .tabs {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
                border-bottom: 1px solid #e5e7eb;
            }
            .tab {
                padding: 8px 0;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                color: #6c757d;
                font-size: 14px;
            }
            .tab.active {
                color: #3b82c4;
                border-bottom-color: #3b82c4;
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #e9ecef;
            }
            .metric-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .metric-card {
                background: white;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid #e5e7eb;
            }
            .metric-label {
                font-size: 12px;
                color: #6c757d;
                text-transform: uppercase;
                margin-bottom: 5px;
            }
            .metric-value {
                font-size: 20px;
                font-weight: 600;
                color: #2c3e50;
            }
            .keyword-list {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            .keyword-tag {
                background: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 13px;
                border: 1px solid #e5e7eb;
            }
            .keyword-density {
                color: #6c757d;
                margin-left: 6px;
            }
            .hidden { display: none; }
            .api-link {
                float: right;
                font-size: 13px;
                color: #6c757d;
                text-decoration: none;
            }
            .api-link:hover {
                color: #3b82c4;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/docs" class="api-link">API Documentation →</a>
            <h1>SEO & Readability Analyzer</h1>
            <p class="subtitle">Analyze webpage content for SEO optimization and readability metrics</p>
            
            <div class="tabs">
                <div class="tab active" onclick="switchTab('url')">URL Analysis</div>
                <div class="tab" onclick="switchTab('text')">Text Analysis</div>
            </div>
            
            <div id="url-tab">
                <div class="input-group">
                    <input type="url" id="url-input" placeholder="Paste URL here" value="">
                    <button onclick="analyzeUrl()">Analyze</button>
                </div>
            </div>
            
            <div id="text-tab" class="hidden">
                <textarea id="text-input" rows="6" placeholder="Paste your text here"></textarea>
                <div style="margin-top: 10px">
                    <button onclick="analyzeText()">Analyze Text</button>
                </div>
            </div>
            
            <div id="results" class="results hidden"></div>
        </div>

        <script>
            function switchTab(tab) {
                const tabs = document.querySelectorAll('.tab');
                const urlTab = document.getElementById('url-tab');
                const textTab = document.getElementById('text-tab');
                
                if (tab === 'url') {
                    tabs[0].classList.add('active');
                    tabs[1].classList.remove('active');
                    urlTab.classList.remove('hidden');
                    textTab.classList.add('hidden');
                } else {
                    tabs[1].classList.add('active');
                    tabs[0].classList.remove('active');
                    textTab.classList.remove('hidden');
                    urlTab.classList.add('hidden');
                }
            }
            
            async function analyzeUrl() {
                const url = document.getElementById('url-input').value.trim();
                if (!url) {
                    alert('Please enter a URL');
                    return;
                }
                
                try {
                    const response = await fetch('/analyze/url', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url: url})
                    });
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    alert('Error analyzing URL');
                }
            }
            
            async function analyzeText() {
                const text = document.getElementById('text-input').value.trim();
                if (!text) {
                    alert('Please enter text');
                    return;
                }
                
                try {
                    const response = await fetch('/analyze/text', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: text})
                    });
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    alert('Error analyzing text');
                }
            }
            
            function displayResults(data) {
                const resultsDiv = document.getElementById('results');
                resultsDiv.classList.remove('hidden');
                
                let keywordsHtml = '';
                data.seo_analysis.top_keywords.forEach(kw => {
                    keywordsHtml += `<div class="keyword-tag">${kw.keyword}<span class="keyword-density">${kw.density_percent}%</span></div>`;
                });
                
                resultsDiv.innerHTML = `
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-label">Word Count</div>
                            <div class="metric-value">${data.metrics.word_count}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Reading Time</div>
                            <div class="metric-value">${data.metrics.estimated_reading_time_minutes} min</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Readability</div>
                            <div class="metric-value">${data.readability.flesch_reading_ease}</div>
                            <div style="font-size: 12px; color: #6c757d; margin-top: 4px">${data.readability.status}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Grade Level</div>
                            <div class="metric-value">${data.readability.grade_level}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Vocabulary Entropy</div>
                            <div class="metric-value">${data.seo_analysis.vocabulary_entropy_score}</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px">
                        <div class="metric-label" style="margin-bottom: 10px">Top Keywords</div>
                        <div class="keyword-list">${keywordsHtml}</div>
                    </div>
                `;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ta  API ENDPOINTS 
@app.post("/analyze/text")
def analyze_raw_text(payload: TextPayload):
    return analyze_content(payload.text)

@app.post("/analyze/url")
def analyze_website_url(payload: UrlPayload):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(payload.url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        analysis = analyze_content(clean_text)
        analysis["scraped_url"] = payload.url
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape URL: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("API IS STARTING ON: http://127.0.0.1:8000")
    print("Swagger UI Docs available at: http://127.0.0.1:8000/docs")
    print("="*50 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)