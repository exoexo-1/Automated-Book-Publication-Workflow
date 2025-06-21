from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_chapter_info(url):
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        content = page.content()
        browser.close()

    soup = BeautifulSoup(content, 'html.parser')

    # --- Extract Book Name, Chapter Info, Author ---
    book_title_tag = soup.select_one('#ws-title a')
    book_title = book_title_tag.text.strip() if book_title_tag else "N/A"

    author_tag = soup.select_one('#ws-author')
    author = author_tag.text.strip() if author_tag else "N/A"


    chapter_info_tag = soup.select_one('#ws-title')
    chapter_info = chapter_info_tag.text.strip().split('—')[-1].strip() if chapter_info_tag else "N/A"



    # --- Extract Actual Chapter Title (usually a subtitle) ---
    chapter_title = "N/A"
    title_div = soup.select_one('.wst-center')
    if title_div:
        title_lines = title_div.stripped_strings
        title_lines = list(title_lines)
        if len(title_lines) >= 3:
            chapter_title = title_lines[2]  # third line is chapter subtitle

    # --- Extract Main Text Content ---
    content_div = soup.select_one('.prp-pages-output')
    if content_div:
        for span in content_div.select(".ws-pagenum"):
            span.decompose()  # remove page numbers
        chapter_text = "\n".join(p.get_text(strip=True) for p in content_div.find_all('p') if p.get_text(strip=True))
    else:
        chapter_text = "N/A"

    return {
        "book_title": book_title,
        "author": author,
        "chapter_info": chapter_info,
        "chapter_title": chapter_title,
        "content": chapter_text
    }

# Run
url = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
chapter_data = extract_chapter_info(url)

# Print
for key, value in chapter_data.items():
    print(f"\n--- {key.upper()} ---\n {value} ")




    