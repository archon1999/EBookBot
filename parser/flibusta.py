import re
import asyncio
import trace
import traceback
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag


BASE_URL = 'https://flibusta.is'


class BookDetail():
    def __init__(self):
        self.id = int()
        self.img = str()
        self.title = str()
        self.author_name = str()
        self.author_id = int()
        self.year_public = str()
        self.tags = list()
        self.description = str()
        self.download_formats = []


class BookList():
    def __init__(self):
        self.id = int()
        self.title = str()
        self.author = str()


async def get_html(url, params=None):
    async with aiohttp.request('GET', url, params=params) as resp:
        if resp.ok:
            return await resp.text()


def parse_book(html) -> BookDetail:
    soup = BeautifulSoup(html, 'lxml')
    book = BookDetail()
    book.title = soup.find(id='main').find('h1', class_='title').text
    if (tag := soup.find(string=re.compile('издание'))):
        text = tag.text.strip()
        book.year_public = re.findall(r'\d{4}', text)[0]

    if (img_tag := soup.find(id='main').find('img', border=None)):
        book.img = img_tag.get('src')

    if (tag := soup.find('h2', string='Аннотация')):
        if (next_sibling := tag.find_next_sibling('p')):
            book.description = next_sibling.text

    book.tags = soup.find(class_='genre').text

    if (author_tag := soup.find(id='main').find(href=re.compile(r'/a/\d'))):
        book.author_name = author_tag.text
        book.author_id = author_tag.get('href').removeprefix('/a/')

    if (tag := soup.find(id='main').find('a', string=re.compile('(следить)'))):
        book.id = tag.get('href').split('/')[-1]

    for download_tag in soup.find(id='main').find_all(
        href=re.compile(f'^/b/{book.id}/')
    ):
        href = download_tag.get('href')
        if href.endswith('read'):
            continue

        name = download_tag.text.strip()
        url = download_tag.get('href')
        format = url.split('/')[-1]
        if format == 'download' and 'pdf' in name:
            format = 'pdf'

        book.download_formats.append((name, format, url))

    return book


async def get_book(book_id) -> BookDetail:
    url = urljoin(BASE_URL, f'b/{book_id}')
    html = await get_html(url)
    book = parse_book(html)
    book.id = book_id
    return book


def parse_book_list(html) -> list[BookList]:
    soup = BeautifulSoup(html, 'lxml')
    tag = soup.find('h3', string=re.compile('Найденные книги'))
    ul_tag = tag.find_next_sibling('ul')
    books = []
    for li_tag in ul_tag.find_all('li'):
        a_tags = li_tag.find_all('a')
        href = a_tags[0].get('href')
        if href and href.startswith('/b/'):
            book = BookList()
            book.id = href.removeprefix('/b/')
            book.title = li_tag.a.text.strip()
            if len(a_tags) > 1:
                book.author = li_tag.find_all('a')[1].text.strip()

            books.append(book)

    return books


async def get_book_list(booksearch) -> list[BookList]:
    params = {'ask': booksearch}
    url = urljoin(BASE_URL, 'booksearch')
    html = await get_html(url, params)
    try:
        book = parse_book(html)
    except Exception:
        pass
    else:
        return [book]

    return parse_book_list(html)


def parse_download_url(html):
    soup = BeautifulSoup(html, 'lxml')
    if (tag := soup.find(class_='p_load_progress_txt')):
        return urljoin(BASE_URL, tag.a.get('href'))


async def book_download(download_url):
    url = urljoin(BASE_URL, download_url)
    async with aiohttp.request('GET', url) as resp:
        if resp.ok:
            return await resp.read()


async def main():
    # print(await book_download('683756', 'fb2.zip'))
    book = await get_book(690769)
    book = await get_book(585918)


asyncio.run(main())
