import requests

# API 엔드포인트 URL
url = 'https://lrib48jimi.execute-api.ap-northeast-2.amazonaws.com/default/test'

# 쿼리 문자열 파라미터 설정
params = {
    'search': '주식'
}

# GET 요청 보내기
response = requests.get(url, params=params)

# JSON 응답을 예상하는 경우
try:
    json_response = response.json()
    print("JSON Response:")
    print(json_response)
except ValueError:
    print("Response is not in JSON format")
