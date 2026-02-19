import re
import os
import asyncio
import requests
from elasticsearch import Elasticsearch
from playwright.async_api import async_playwright
es = Elasticsearch("http://localhost:9200")

PDF_FOLDER = os.path.join(os.path.dirname(__file__), "pdfs")
os.makedirs(PDF_FOLDER, exist_ok=True)


def get_year_from_url(url: str) -> str:
    match = re.search(r"@(\d{4})-\d{2}-\d{2}$", url)
    return match.group(1) if match else None

def download_pdf(pdf_url: str, filename: str):

    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()

        file_path = os.path.join(PDF_FOLDER, filename)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded PDF: {file_path}")
    except Exception as e:
        print(f"Failed to download {pdf_url}: {e}")



async def crawl_acts():
    async with async_playwright() as p:

        bills_browser = await p.chromium.launch(headless=True)

        page = await bills_browser.new_page()

        await page.goto("https://new.kenyalaw.org/legislation/", wait_until="domcontentloaded", timeout=60000)

        links = await page.locator("td.cell-title > a").all()

        for link in links[:100]:
            href = await link.get_attribute("href")

            full_url = 'https://new.kenyalaw.org' + href

            detail_page = await bills_browser.new_page()

            await detail_page.goto(full_url,wait_until="domcontentloaded", timeout=60000)

            await detail_page.wait_for_load_state("networkidle")

            title = await detail_page.locator("h1").first.inner_text()
            last_revision_date = await detail_page.locator(".card-header h5.mb-0").first.inner_text()
            fulltext = await detail_page.locator(".content-and-enrichments__inner").first.inner_text()

            doc = {
                "title": title,
                "year": get_year_from_url(full_url) or "2026",
                "last_revision_date": last_revision_date.split("\n")[1].strip(),
                "url": full_url,
                "pdf_source": full_url + "/source",
                "full_text": fulltext,
                "full_text_length": fulltext,
            }

            es.index(index="my-index", document=doc)

            await detail_page.close()

            download_pdf(doc['pdf_source'], f"{doc['title'].replace(' ', '_')}.pdf")

        await bills_browser.close()

asyncio.run(crawl_acts())

