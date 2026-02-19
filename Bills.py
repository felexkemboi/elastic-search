import asyncio
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


async def crawl_bills():
    async with async_playwright() as p:

        bills_browser = await p.chromium.launch(headless=True)

        page = await bills_browser.new_page()

        await page.goto("https://new.kenyalaw.org/bills/")

        links = await page.locator("td.cell-title > a").all()

        for link in links[:30]:
            href = await link.get_attribute("href")
            print('https://new.kenyalaw.org' + href)

        await bills_browser.close()

asyncio.run(crawl_bills())
