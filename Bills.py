import asyncio
from datetime import datetime
import re
from elasticsearch import Elasticsearch
from playwright.async_api import async_playwright
es = Elasticsearch("http://localhost:9200")

# # Check connection
# if es.ping():
#     print("Connected to Elasticsearch!")
# else:
#     print("Could not connect to Elasticsearch")

# # Example data to index
# doc = {
#     "title": "My first document",
#     "content": "This is some text",
#     "timestamp": "2026-02-18"
# }

# # Index the document into "my-index"
# res = es.index(index="my-index", document=doc)

# print(res)

# print("Document indexed:", res['result'])


# async def crawl_bills_urls():
#     async with async_playwright() as p:

#         bills_browser = await p.chromium.launch(headless=True)

#         page = await bills_browser.new_page()

#         await page.goto("https://new.kenyalaw.org/bills/")

#         links = await page.locator("td.cell-title > a").all()

#         for link in links[:30]:
#             href = await link.get_attribute("href")
#             print('https://new.kenyalaw.org' + href)

#         await bills_browser.close()

def get_year_from_url(url: str) -> str:
    """
    Extract year from the @YYYY-MM-DD part of a Kenya Law act/regulation URL.
    Returns None if no match is found.
    """
    match = re.search(r"@(\d{4})-\d{2}-\d{2}$", url)
    return match.group(1) if match else None


async def crawl_acts_urls():
    async with async_playwright() as p:

        bills_browser = await p.chromium.launch(headless=True)

        page = await bills_browser.new_page()

        await page.goto("https://new.kenyalaw.org/legislation/", wait_until="domcontentloaded", timeout=60000)

        links = await page.locator("td.cell-title > a").all()

        for link in links[:30]:
            href = await link.get_attribute("href")

            full_url = 'https://new.kenyalaw.org' + href

            detail_page = await bills_browser.new_page()

            await detail_page.goto(full_url,wait_until="domcontentloaded", timeout=60000)

            await detail_page.wait_for_load_state("networkidle")

            title = await detail_page.locator("h1").first.inner_text()
            last_revision_date = await detail_page.locator(".card-header h5.mb-0").first.inner_text()
            last_revision_date = datetime.strptime(last_revision_date, "%d %B %Y").strftime("%Y-%m-%d")

            print("Year:", get_year_from_url(full_url))
            print("Last Revision Date:", last_revision_date)
            print("Title:", title)
            print("URL:", full_url)
            print("PDF Source:", full_url+ "/source")

            print("")

            await detail_page.close()

        await bills_browser.close()

# asyncio.run(crawl_bills_urls())
asyncio.run(crawl_acts_urls())

