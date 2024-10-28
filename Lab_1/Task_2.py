import re

def parse_products(html_content):
    products = []

    # Regex pattern to extract product divs
    product_pattern = re.compile(r'<div class="product-grid-item.*?<\/div>', re.DOTALL)

    for product_div in product_pattern.findall(html_content):
        print("Processing product div: ", product_div)  # Debugging

        # Extract name
        name_match = re.search(r'<h4 class="name"><a[^>]*>(.*?)<\/a><\/h4>', product_div)
        name = name_match.group(1).strip() if name_match else "Unknown"
        print("Extracted name: ", name)  # Debugging

        # Extract description
        description_match = re.search(r'<p class="description">(.*?)<\/p>', product_div)
        description = description_match.group(1).strip() if description_match else "No description available"
        print("Extracted description: ", description)  # Debugging

        # Extract prices
        price_new_match = re.search(r'<span class="price-new">(.*?)<\/span>', product_div)
        price_old_match = re.search(r'<span class="price-old">(.*?)<\/span>', product_div)

        price_new = price_new_match.group(1).strip() if price_new_match else "0 Lei"
        price_old = price_old_match.group(1).strip() if price_old_match else "0 Lei"
        print("Extracted prices: new =", price_new, ", old =", price_old)  # Debugging

        # Convert prices to float
        price_new_float = float(price_new.replace(' Lei', '').replace('.', '').replace(',', '.'))
        price_old_float = float(price_old.replace(' Lei', '').replace('.', '').replace(',', '.'))

        # Create a product ID (incremental)
        product_id = len(products) + 1

        products.append({
            'id': product_id,
            'name': name,
            'description': description,
            'price': price_new_float,
            'price_old': price_old_float
        })

    return products

# Sample HTML content (replace with your actual HTML)
html_content = """
<div class="product-grid-item xs-50 sm-33 md-33 lg-25 xl-20">
    <div class="product-thumb product-wrapper ">
        <div class="image ">
            <a href="#">
                <img class="lazy first-image" width="250" height="250" src="image.png" />
            </a>
        </div>
        <div class="product-details">
            <div class="caption">
                <h4 class="name"><a href="#">Product Name Example</a></h4>
                <p class="description">This is a sample description for the product.</p>
                <p class="price">
                    <span class="price-old">200.00 Lei</span>
                    <span class="price-new">100.00 Lei</span>
                </p>
            </div>
        </div>
    </div>
</div>
"""

# Call the function and print results
products = parse_products(html_content)
for product in products:
    print(product)
