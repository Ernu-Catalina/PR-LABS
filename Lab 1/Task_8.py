import socket
import ssl
from bs4 import BeautifulSoup

# Function to send HTTPS requests and get HTML content
def send_https_request(host, path):
    context = ssl.create_default_context()
    sock = socket.create_connection((host, 443))
    secure_sock = context.wrap_socket(sock, server_hostname=host)

    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    secure_sock.sendall(request.encode())

    response = b""
    while True:
        data = secure_sock.recv(4096)
        if not data:
            break
        response += data

    secure_sock.close()
    response_str = response.decode()

    headers, body = response_str.split("\r\n\r\n", 1)
    return body

# Function to parse products from HTML content
def parse_products(html):
    products = []
    soup = BeautifulSoup(html, 'html.parser')
    product_divs = soup.find_all('div', class_='product-grid-item')

    for product_div in product_divs:
        product_link = product_div.find('a')['href']
        product_image = product_div.find('img')['src']

        name = product_div.find('img')['alt'] if product_div.find('img') else "Unknown"
        description = product_div.find('h4').get_text(strip=True) if product_div.find('h4') else "No description available"

        price_info = product_div.find('p', class_='price')
        new_price = None
        old_price = None

        if price_info:
            price_text = price_info.get_text(strip=True)
            price_parts = price_text.split(' ')
            for part in price_parts:
                if 'old' in part.lower():
                    old_price_str = part.replace('Old:', '').replace('€', '').strip()
                    try:
                        old_price = float(old_price_str)
                    except ValueError:
                        old_price = None
                elif 'price' in part.lower():
                    new_price_str = part.replace('Price:', '').replace('€', '').strip()
                    try:
                        new_price = float(new_price_str)
                    except ValueError:
                        new_price = None

        product = {
            'link': product_link,
            'image': product_image,
            'name': name,
            'description': description,
            'new_price': new_price,
            'old_price': old_price,
        }
        products.append(product)
        print(f"Processed product: {name}, Description: {description}, New Price: {new_price}, Old Price: {old_price}")

    return products

# Function to serialize data to JSON format
def serialize_to_json(products):
    json_output = "["
    for product in products:
        product_json = f"""{{
            "link": "{product['link']}",
            "image": "{product['image']}",
            "name": "{product['name']}",
            "description": "{product['description']}",
            "new_price": {product['new_price'] if product['new_price'] is not None else 'null'},
            "old_price": {product['old_price'] if product['old_price'] is not None else 'null'}
        }}"""
        json_output += product_json + ","
    json_output = json_output.rstrip(',') + "]"  # Remove trailing comma
    print("JSON Output:")
    print(json_output)

# Function to serialize data to XML format
def serialize_to_xml(products):
    xml_output = "<products>\n"
    for product in products:
        xml_output += f"  <product>\n"
        xml_output += f"    <link>{product['link']}</link>\n"
        xml_output += f"    <image>{product['image']}</image>\n"
        xml_output += f"    <name>{product['name']}</name>\n"
        xml_output += f"    <description>{product['description']}</description>\n"
        xml_output += f"    <new_price>{product['new_price'] if product['new_price'] is not None else 'null'}</new_price>\n"
        xml_output += f"    <old_price>{product['old_price'] if product['old_price'] is not None else 'null'}</old_price>\n"
        xml_output += f"  </product>\n"
    xml_output += "</products>"
    print("XML Output:")
    print(xml_output)

# Main execution
host = 'educationalcentre.md'
path = '/shop/index.php?route=product/category&path=2350_2355_2361'
html_content = send_https_request(host, path)
products = parse_products(html_content)

# Serialize products to JSON and XML
serialize_to_json(products)
serialize_to_xml(products)
