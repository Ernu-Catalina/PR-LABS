import socket
import ssl
import re
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


# Function to send HTTPS request and get the HTML content
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


# Function to parse the HTML and extract product data
def parse_html(html):
    product_pattern = re.compile(r'<h4 class="name"><a href="(?P<url>[^"]+)">(?P<name>[^<]+)</a></h4>')
    price_pattern = re.compile(r'<span class="price-old">(?P<old_price>[^<]+)</span> <span class="price-new"[^>]*>(?P<new_price>[^<]+)</span>')

    products = []
    for product_match in product_pattern.finditer(html):
        product_info = product_match.groupdict()

        # Search for prices associated with this product
        price_match = price_pattern.search(html, product_match.end())
        if price_match:
            product_info.update(price_match.groupdict())
        else:
            product_info['old_price'] = None
            product_info['new_price'] = None

        products.append(product_info)

    return products


# Function to generate JSON from product data
def generate_json(products):
    return json.dumps(products, indent=4)


# Function to generate XML from product data
def generate_xml(products):
    root = ET.Element("products")

    for product in products:
        product_elem = ET.SubElement(root, "product")

        name_elem = ET.SubElement(product_elem, "name")
        name_elem.text = product["name"]

        url_elem = ET.SubElement(product_elem, "url")
        url_elem.text = product["url"]

        old_price_elem = ET.SubElement(product_elem, "old_price")
        old_price_elem.text = product["old_price"] if product["old_price"] else "N/A"

        new_price_elem = ET.SubElement(product_elem, "new_price")
        new_price_elem.text = product["new_price"] if product["new_price"] else "N/A"

    return root


# Function to pretty-print the XML
def pretty_print_xml(element):
    rough_string = ET.tostring(element, encoding='utf8', method='xml')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


# Host and path to send the request to
host = 'educationalcentre.md'
path = '/shop/index.php?route=product/category&path=2350_2355_2361'

# Fetch the HTML content
html_content = send_https_request(host, path)

# Parse the HTML to extract product information
products = parse_html(html_content)

# Generate JSON and XML from the product data
json_output = generate_json(products)
xml_tree = generate_xml(products)
xml_output = pretty_print_xml(xml_tree)

# Print the JSON and XML output
print("JSON Output:\n", json_output)
print("\nXML Output:\n", xml_output)
