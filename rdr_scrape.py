import requests, csv, time, re, logging
from bs4 import BeautifulSoup

logger = logging.Logger('catch_all')

DEST_FILE = 'rdr_data2.csv'

def get_word_count(title):
    """Extracts the word count from the post title.
    Posts on r/DestructiveReaders put their word counts in square brackets.
    """
    nums = ""
    begin = False
    for j in title:
        if begin:
            if j == "]":
                break
            if j.isdigit():
                nums += j
        elif j == "[":
            begin = True
    return int(nums) if nums else -1


def process_title(title):
    title = title.replace("(self.DestructiveReaders)", "")
    return re.sub(r'[^A-Za-z0-9 \[\]().!?,;:]+', '', title)

def process_genre(genre):
    """Many of the genres are DIY. This collapses them down to a few major
     headings, else 'other'. The headings are 'fantasy', 'meta', 'scifi',
     'horror', 'contemporary', 'cyberpunk', 'ya', 'crime', 'poetry',
     'other', 'flash', 'superhero', 'thriller', 'play', and 'non-fiction'.
     """

    big_list = {'fantasy': 'fantasy', 'urban fantasy': 'fantasy', 'meta': 'meta',
                'sci - fi': 'scifi', 'horror': 'horror', 'science fiction': 'scifi',
                'contemporary / dramedy': 'contemporary', 'cyberpunk': 'cyberpunk',
                'ya fantasy': 'ya',
                'southern - fried paranormal detective story': 'crime',
                'lit fic': 'contemporary', 'poetry': 'poetry', 'sci fi': 'scifi',
                'scifi': 'scifi', 'dark fantasy': 'fantasy', 'litfic': 'contemporary',
                'non - fiction': 'non-fiction', 'flash fiction': 'flash',
                'literary fiction': 'contemporary', 'modern fantasy': 'fantasy',
                'sci - fi / fantasy': 'scifi', 'suspense': 'crime',
                'contemporary': 'contemporary', 'fantasy romance': 'fantasy',
                'fiction': 'contemporary', 'high fantasy': 'fantasy',
                'horror short story': 'horror', 'speculative fiction': 'scifi',
                'ya fiction': 'ya', 'collaborative superhero fiction': 'superhero',
                'crime': 'crime', 'fantasy(short)': 'fantasy',
                'historical fiction': 'historical', 'horror(short story)': 'horror',
                'literary': 'literary', 'low fantasy': 'fantasy',
                'magic realism': 'fantasy', 'microfiction': 'flash',
                'murder mystery': 'crime', 'murder mystery / war': 'crime',
                'mystery': 'crime', 'paranormal thriller': 'thriller',
                'play': 'play', 'psychological thriller': 'thriller',
                'query': 'query', 'realistic': 'contemporary',
                'sci - fi / drama': 'scifi', 'sci - fi adventure': 'scifi',
                'science fantasy': 'scifi',
                'science fiction(short story)': 'scifi',
                'short story / non - fiction': 'non-fiction',
                'short story / magical realism': 'fantasy',
                'supernatural / future': 'scifi', 'techno thriller': 'thriller',
                'ya dystopian': 'ya'}

    if genre in big_list:
        return big_list[genre]
    else:
        return 'other'


def main():
    url = "https://old.reddit.com/r/DestructiveReaders/"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}

    page = requests.get(url, headers=headers)

    counter = 1

    post_line = []

    with open(DEST_FILE, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Index", "Title", "Author", "Likes", "Comments", "WordCount", "Genre", "Date"])

    while counter < 950:

        print(counter)

        soup = BeautifulSoup(page.text, 'html.parser')

        attrs = {'class': 'thing', 'data-domain': 'self.DestructiveReaders'}

        posts = soup.find_all("div", attrs=attrs)

        for post in posts:
            try:
                title = process_title(post.find('p', class_="title").text)
                word_count = get_word_count(title)
                try:
                    author = post.find('a', class_='author').text
                except AttributeError:
                    author = "deleted"
                comments = post.find('a', class_='comments').text.split()[0]
                if comments == "comment":
                    comments = 0
                likes = post.find('div', attrs={'class': "score likes"}).text
                if likes == "•":
                    likes = "-1"
                try:
                    genre = post.find('span', class_='linkflairlabel').text
                    title = title.replace(genre, "")
                    genre = genre.lower()
                    # genre = process_genre(genre.lower())
                except AttributeError:
                    genre = 'other'
                date = post.find('time')['datetime'][:10]
                post_line = [counter, title, author, likes, comments, word_count, genre, date]
                try:
                    with open(DEST_FILE, 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(post_line)
                except Exception as e:
                    print("writing problem")
                    print(post_line)
                    logger.error(str(e))
                    continue

            except Exception as e:
                print("Big Confusing Problem")
                print(post_line)
                logger.error(str(e))

            counter += 1

        next_button = soup.find("span", class_="next-button")

        next_page_link = next_button.find("a").attrs['href']

        print(next_page_link)

        time.sleep(4)

        page = requests.get(next_page_link, headers=headers)


main()
