import urllib.request
import ssl

def check_url(url):
    print(f"Checking: {url}")
    try:
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as response:
            if response.status == 200:
                print("  -> SUCCESS")
                return True
    except Exception as e:
        print(f"  -> FAILED: {e}")
    return False

base_patterns = [
    "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/search/materialiconsrounded/48dp/2x/baseline_search_black_48dp.png",
    "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/search/materialicons/48dp/2x/baseline_search_black_48dp.png",
    "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/search/materialiconsoutlined/48dp/2x/baseline_search_black_48dp.png",
    "https://raw.githubusercontent.com/google/material-design-icons/3.0.1/png/action/search/materialicons/48dp/2x/baseline_search_black_48dp.png",
    "https://raw.githubusercontent.com/google/material-design-icons/master/src/action/search/materialiconsrounded/24px.svg",
]

for url in base_patterns:
    if check_url(url):
        break
