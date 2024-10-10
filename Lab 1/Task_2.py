import requests

url = 'https://educationalcentre.md/shop/index.php?route=product/category&path=2350_2355_2361'

response = requests.get(url)

if response.status_code == 200:
    print(response.text)
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
