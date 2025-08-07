import requests
import json
import base64
import os

# ------------------ CONFIG (Github Secrets as ENV) -------------------

AUTH_TOKEN = os.environ.get("SCANX_AUTH_TOKEN")
AUTHORISATION_TOKEN = os.environ.get("SCANX_AUTHORIZATION_TOKEN")
WP_SITE_URL = os.environ.get("WP_SITE_URL")
POST_ID = os.environ.get("WP_POST_ID")
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_APPLICATION_PASSWORD = os.environ.get("WP_APPLICATION_PASSWORD")

payload = {
    "categories": ["ALL"],
    "entity_id": "9971029164",
    "first_news_timeStamp": 0,
    "last_news_timeStamp": 0,
    "limit": 50,
    "news_feed_type": "live",
    "page_no": 0,
    "stock_list": []
}
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Auth": AUTH_TOKEN,
    "Authorisation": AUTHORISATION_TOKEN,
    "Origin": "https://scanx.trade"
}
URL = "https://news-live.dhan.co/v3/news/getLiveNews"

def truncate_text(text, max_len):
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    if ' ' in truncated:
        truncated = truncated[:truncated.rfind(' ')]
    return truncated + "..."

def create_news_widget_html(news_items):
    html = '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    .luxury-news-widget {
        max-width: 720px;
        margin: 30px auto;
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 20px 50px 0 rgba(19, 84, 115, 0.24), 0 4px 15px 0 rgba(19, 84, 115, 0.11);
        font-family: 'Poppins', sans-serif;
        color: #222;
        padding: 30px 40px 40px 40px;
        user-select: none;
    }
    .luxury-news-card {
        border-radius: 17px;
        box-shadow: 0 8px 30px rgba(19, 84, 115, 0.11);
        padding: 24px 28px 26px 28px;
        margin-bottom: 28px;
        background: linear-gradient(135deg, #f0f5f8 0%, #e6ecf2 100%);
        border-left: 6px solid #135473;
        transition: box-shadow 0.3s, border-left 0.3s, background 0.3s;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    .luxury-news-card:hover {
        box-shadow: 0 22px 66px 0 rgba(19, 84, 115, 0.22);
        border-left: 6px solid #135473;
        background: linear-gradient(135deg, #e3edf4 0%, #c6d9e6 100%);
        transform: scale(1.02) translateY(-3px);
    }
    .luxury-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 15px;
    }
    .luxury-title {
        font-weight: 700;
        font-size: 1.35rem;
        line-height: 1.3;
        color: #135473;
        letter-spacing: 0.02em;
        flex: 1 1 auto;
        margin-right: 16px;
        text-shadow: 0 2px 6px rgba(19,84,115,0.07);
    }
    .luxury-sentiment {
        font-weight: 700;
        font-size: 0.99rem;
        line-height: 1.1;
        min-width: 92px;
        text-align: center;
        border-radius: 14px;
        padding: 6px 14px;
        user-select: text;
        border: 1.5px solid #13547333;
        background: #e6ecf2;
        letter-spacing: .03em;
        transition: background 0.3s, color 0.25s, border-color 0.3s;
    }
    .luxury-sentiment.positive {
        color: #0ab547;
        border-color: #0ab54755;
        background: #ecf9f2;
    }
    .luxury-sentiment.negative {
        color: #e74c3c;
        border-color: #e74c3c55;
        background: #fff4f2;
    }
    .luxury-sentiment.neutral {
        color: #f39c12;
        border-color: #f39c1255;
        background: #fffbe7;
    }
    .luxury-description {
        font-weight: 400;
        font-size: 1rem;
        line-height: 1.5;
        color: #27425b;
        max-height: 4.2em;
        text-overflow: ellipsis;
        overflow: hidden;
        transition: max-height 0.5s, padding 0.5s;
        cursor: pointer;
        border-radius: 12px;
        padding: 0 2px;
        background: transparent;
    }
    .luxury-description.expanded {
        max-height: 1000px;
        padding-top: 8px;
        background: #f2f8fc;
        box-shadow: 0 4px 12px 0 rgba(19,84,115,0.03);
    }
    .luxury-stock {
        margin-top: 14px;
        font-weight: 600;
        font-size: 0.98rem;
        color: #135473;
        background: #deeef8;
        padding: 6px 18px;
        display: inline-block;
        border-radius: 22px;
        letter-spacing: 0.03em;
        box-shadow:  0 1px 6px 0 rgba(19,84,115,0.08);
        user-select: text;
    }
    .luxury-poweredby {
        text-align: right;
        font-size: 0.77rem;
        color: #7fa0b8;
        margin-top: 18px;
        font-weight: 600;
        letter-spacing: 0.06em;
        font-style: italic;
    }
    </style>
    <div class="luxury-news-widget">
    '''
    for idx, item in enumerate(news_items, 1):
        n_obj = item.get("news_object", {})
        title = n_obj.get("title", "No Title Provided").replace('`', "'")
        description = n_obj.get("text", "").replace('`', "'").replace('\n', '<br>')
        sentiment = n_obj.get("overall_sentiment", "neutral").lower()
        stock_name = item.get("stock_name", "Unknown Stock")
        sentiment_text = "Neutral"
        sentiment_class = "neutral"
        if sentiment == "positive":
            sentiment_text = "Positive"
            sentiment_class = "positive"
        elif sentiment == "negative":
            sentiment_text = "Negative"
            sentiment_class = "negative"
        html += f'''
        <div class="luxury-news-card" onclick="toggleDescription('desc-{idx}')">
            <div class="luxury-header">
                <div class="luxury-title">{title}</div>
                <div class="luxury-sentiment {sentiment_class}">{sentiment_text}</div>
            </div>
            <div id="desc-{idx}" class="luxury-description">{truncate_text(description, 150)}</div>
            <div class="luxury-stock">Impact: {stock_name}</div>
        </div>
        <script>
            window['desc-{idx}-full'] = `{description}`;
            window['desc-{idx}-collapsed'] = `{truncate_text(description, 150)}`;
        </script>
        '''
    html += '''
        <div class="luxury-poweredby">News Widget Powered by ScanX &amp; Developed By You</div>
    </div>
    <script>
    function toggleDescription(id) {
        var el = document.getElementById(id);
        if (!el) return;
        if (el.classList.contains('expanded')) {
            el.classList.remove('expanded');
            el.innerHTML = window[id + '-collapsed'];
        } else {
            el.classList.add('expanded');
            el.innerHTML = window[id + '-full'];
        }
    }
    document.addEventListener('DOMContentLoaded', function () {
        var cards = document.querySelectorAll('.luxury-description');
        cards.forEach(function(card){
            var id = card.id;
            card.innerHTML = window[id + '-collapsed'];
            card.classList.remove('expanded');
        });
    });
    </script>
    '''
    return html

def publish_to_wordpress(wp_site_url, post_id, wp_username, wp_application_password, html_content):
    wp_url = f"{wp_site_url}/wp-json/wp/v2/posts/{post_id}"
    creds = f"{wp_username}:{wp_application_password}"
    token = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
    post_data = {
        "content": html_content,
        "status": "publish"
    }
    response = requests.post(wp_url, headers=headers, data=json.dumps(post_data))
    if response.status_code in [200, 201]:
        print("✅ WordPress Post Updated Successfully!")
        print("URL:", response.json().get('link'))
    else:
        print(f"❌ Failed to update WordPress Post: {response.status_code} - {response.text}")

def main():
    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching data from ScanX API:", e)
        return
    try:
        data = response.json()
    except Exception as e:
        print("Error decoding JSON:", e)
        print("Raw response:", response.text)
        return

    news_list = data.get("data", {}).get("latest_news", [])
    if not news_list:
        print("No news available.")
        return
    html_output = create_news_widget_html(news_list)
    publish_to_wordpress(WP_SITE_URL, POST_ID, WP_USERNAME, WP_APPLICATION_PASSWORD, html_output)

if __name__ == "__main__":
    main()