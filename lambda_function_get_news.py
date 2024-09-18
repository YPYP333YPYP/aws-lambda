import json
import os
import logging

import openai
import requests
import dotenv
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dotenv.load_dotenv()


def get_news_from_naver(query):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=100"
    headers = {
        "X-Naver-Client-Id": os.getenv("X-Naver-Client-Id"),
        "X-Naver-Client-Secret": os.getenv("X-Naver-Client-Secret")
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        filtered_items = [
            item['link'] for item in data['items']
            if item['link'].startswith('https://n.news.naver.com')
        ]
        return filtered_items[:5]
    else:
        raise Exception("naver")


def scrape_article(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('div', id='newsct_article')
        if article:
            content = article.get_text(separator='\n', strip=True)
            return content
    return None


def get_article(news_links):
    articles = ""
    for link in news_links:
        article = scrape_article(link)
        if article:
            articles += article + "\n"
    return articles or ""


def summarize_article(article, query):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not article.strip():  # 빈 문자열이나 공백 문자열인 경우
        return "No content to summarize"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"{query}를 핵심으로 생각하면서 뉴스 기사를 200자 이내로 요약해"},
                {"role": "user", "content": article}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"An error occurred: {str(e)}"


def lambda_handler(event, context):
    logger.info("Lambda function has started")


    try:
        query_params = event.get('queryStringParameters', {})
        search = query_params.get('search')
        news_links = get_news_from_naver(search)
        article_content = get_article(news_links)
        summary = summarize_article(article_content, search)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'query': search,
                'summary': summary
            }, ensure_ascii=False)
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

