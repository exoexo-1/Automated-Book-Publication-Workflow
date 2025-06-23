# main.py

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from save import save_chapter_auto_version

def extract_chapter_info(url):
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path="screenshot.png")
        content = page.content()
        browser.close()

    soup = BeautifulSoup(content, 'html.parser')

    book_title_tag = soup.select_one('#ws-title a')
    book_title = book_title_tag.text.strip() if book_title_tag else "N/A"

    author_tag = soup.select_one('#ws-author')
    author = author_tag.text.strip() if author_tag else "N/A"

    chapter_info_tag = soup.select_one('#ws-title')
    chapter_info = chapter_info_tag.text.strip().split('—')[-1].strip() if chapter_info_tag else "N/A"

    chapter_title = "N/A"
    title_div = soup.select_one('.wst-center')
    if title_div:
        lines = list(title_div.stripped_strings)
        if len(lines) >= 3:
            chapter_title = lines[2]

    content_div = soup.select_one('.prp-pages-output')
    if content_div:
        for span in content_div.select(".ws-pagenum"):
            span.decompose()
        chapter_text = "\n".join(p.get_text(strip=True) for p in content_div.find_all('p') if p.get_text(strip=True))
    else:
        chapter_text = "N/A"

    return {
        "book_title": book_title,
        "author": author,
        "chapter_info": chapter_info,
        "chapter_title": chapter_title,
        "content": chapter_text,
        "source_url": url
    }


if __name__ == "__main__":
    url = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
    data = extract_chapter_info(url)
    save_chapter_auto_version(data, base_id="chapter1",stage= "raw")
