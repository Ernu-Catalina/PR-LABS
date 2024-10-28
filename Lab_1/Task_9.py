import socket
import ssl
import re


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
    product_pattern = re.compile(
        r'<div class="product-grid-item.*?">.*?'
        r'<h4 class="name"><a href="(?P<url>[^"]+)">(?P<name>.*?)</a></h4>.*?'
        r'<p class="description">(?P<description>.*?)</p>.*?'
        r'<span class="price-old">(?P<old_price>[^<]+)</span>.*?'
        r'<span class="price-new"[^>]*>(?P<new_price>[^<]+)</span>',
        re.DOTALL
    )

    products = []
    for product_match in product_pattern.finditer(html):
        product_info = product_match.groupdict()
        products.append(product_info)

    return products


# Custom serialization function
def serialize_products(products):
    serialized_data = []
    for product in products:
        serialized_line = (
            f"Product Name: {product['name']}\n"
            f"Price: {product['new_price']}\n"
            f"Description: {product['description']}\n"
            f"{'-' * 30}\n"  # Separator for clarity
        )
        serialized_data.append(serialized_line)
    return ''.join(serialized_data)


# Custom deserialization function to create object representation
def deserialize_products(serialized_data):
    products = []
    product_blocks = serialized_data.strip().split('-' * 30)

    for block in product_blocks:
        if block.strip():  # Check if the block is not empty
            lines = block.strip().splitlines()
            if len(lines) >= 3:
                name = lines[0].replace("Product Name: ", "").strip()
                price = lines[1].replace("Price: ", "").strip()
                description = lines[2].replace("Description: ", "").strip()

                # Create a product object as a dictionary
                products.append({
                    'name': name,
                    'price': price,
                    'description': description
                })
            else:
                print(f"Skipping invalid block: {block.strip()}")  # Handle any malformed blocks
    return products


# Host and path to send the request to
host = 'educationalcentre.md'
path = '/shop/index.php?route=product/category&path=2350_2355_2361'

# Fetch the HTML content
html_content = send_https_request(host, path)

# Parse the HTML to extract product information
products = parse_html(html_content)

# Serialize the product data
serialized_output = serialize_products(products)
print("Serialized Output:\n", serialized_output)

# Deserialize the product data into object representation
deserialized_products = deserialize_products(serialized_output)

# Print the reconstructed object representation of products
print("\nReconstructed Products as Objects:")
for product in deserialized_products:
    print(f"Name: {product['name']}, Price: {product['price']}, Description: {product['description']}")
