from requests import get

SEARCH_BASE: str = 'https://api.mangadex.org/manga?title='
SEARCH_PARAM: str = '&limit=5&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&includes[' \
                    ']=cover_art&order[relevance]=desc'
CHAPTER_SEARCH_BASE: str = 'https://api.mangadex.org/manga/'
CHAPTER_SEARCH_PARAM: str = '/feed?limit=96&includes[]=scanlation_group&includes[]=user&order[volume]=desc&order[' \
                            'chapter]=desc&offset=0&contentRating[]=safe&contentRating[]=suggestive&contentRating[' \
                            ']=erotica&contentRating[]=pornographic'


def search_work(title: str) -> list:
    result: dict = get(SEARCH_BASE + title + SEARCH_PARAM).json()

    data_list: list = result["data"]

    result_list = ["Total: {}".format(len(data_list))]
    for item in data_list:
        result_list.append({"title": item["attributes"]["title"]["en"], "genre": item["type"], "id": item["id"]})

    return result_list


def search_chapters(work_hash: str) -> list:
    result: dict = get(CHAPTER_SEARCH_BASE + work_hash + CHAPTER_SEARCH_PARAM).json()

    chapter_list: list = []

    for item in result["data"]:
        if item['attributes']['translatedLanguage'] == 'en':
            chapter_list.append([item['id'], f"Chapter {item['attributes']['chapter']}"])

    # The sequence of MangaDex in reversed (e.g. 10, 9, 8, 7....)

    chapter_list.reverse()
    chapter_list.insert(0, 'Total: {}'.format(len(chapter_list)))

    return chapter_list
