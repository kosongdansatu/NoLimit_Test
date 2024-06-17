import requests
from bs4 import BeautifulSoup
import json
import sys
import os
from datetime import datetime


def scrape_wikipedia(phrase, proxy_url=None):
    # Format URL untuk pencarian Wikipedia
    search_url = f"https://en.wikipedia.org/wiki/{phrase.replace(' ', '_')}"

    # Setup proxy jika diberikan
    proxies = (
        {
            "http": proxy_url,
            "https": proxy_url,
        }
        if proxy_url
        else None
    )

    try:
        # Mengirimkan permintaan HTTP ke Wikipedia
        response = requests.get(search_url, proxies=proxies, timeout=10)

        # Mengecek apakah permintaan berhasil
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return

        # Parsing konten HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # Menemukan elemen konten utama Wikipedia
        content = soup.find(id="mw-content-text")
        paragraphs = content.find_all("p")

        # Menggabungkan teks dari semua paragraf
        text = "\n".join([para.get_text() for para in paragraphs])

        # Mendapatkan judul artikel
        title = soup.find(id="firstHeading").text

        # Mendapatkan kategori artikel jika ada
        category = soup.find(id="mw-normal-catlinks")
        category = category.find_all("a")[1].text if category else "Uncategorized"

        # Mendapatkan waktu saat ini dalam format yang ditentukan
        created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        # Menyiapkan data untuk disimpan ke dalam file JSON
        data = [
            {
                "title": title,
                "link": search_url,
                "content": text,
                "createdAt": created_at,
                "category": category,
            }
        ]

        # Menentukan nama file JSON
        json_filename = f"{phrase.replace(' ', '_')}.json"

        # Mengecek apakah file sudah ada
        if os.path.exists(json_filename):
            print(f"File {json_filename} already exists. Not overwriting.")
            return

        # Menyimpan data ke dalam file JSON
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        print(f"Data successfully saved to {json_filename}")

    except requests.exceptions.ProxyError as e:
        print(f"Proxy error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"Request timed out: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run_scraper.sh [phrase] [proxy_url]")
        sys.exit(1)

    phrase = sys.argv[1]
    proxy_url = sys.argv[2] if len(sys.argv) > 2 else None

    scrape_wikipedia(phrase, proxy_url)
