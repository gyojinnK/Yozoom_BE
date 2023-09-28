from django.http import HttpResponse, JsonResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_craw(request):
    options = webdriver.ChromeOptions()
    # 창이 나타나지 않도록 Headless 설정
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 이용하려는 URL
    url = 'http://ncov.kdca.go.kr/'

    driver.get(url)

    topnews = driver.find_element('xpath','//*[@id="content"]/div[3]/div/div/div[2]/div[2]/div/ul[2]/li[1]/strong')

    return JsonResponse({'Value': topnews.text})