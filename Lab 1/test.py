def parse_products(html):
    products = []

    # Look for simple patterns in the HTML content
    product_section = html.split('<div class="product-grid-item">')

    if len(product_section) <= 1:
        print("No products found in the HTML.")
    else:
        print(f"Found {len(product_section) - 1} product sections.")

    for section in product_section[1:]:
        # Debug to verify sections
        print("Processing product section...")
        print(section[:500])  # Print a portion of the product section for verification

        link_start = section.find('href="') + len('href="')
        link_end = section.find('"', link_start)
        product_link = section[link_start:link_end]

        img_start = section.find('src="') + len('src="')
        img_end = section.find('"', img_start)
        product_image = section[img_start:img_end]

        name_start = section.find('alt="') + len('alt="')
        name_end = section.find('"', name_start)
        product_name = section[name_start:name_end] if 'alt="' in section else "Unknown"

        desc_start = section.find('<h4>') + len('<h4>')
        desc_end = section.find('</h4>', desc_start)
        product_description = section[desc_start:desc_end].strip() if '<h4>' in section else "No description available"

        # Extracting prices
        new_price = None
        old_price = None
        price_section = section.split('<p class="price">')
        if len(price_section) > 1:
            price_text = price_section[1].split('</p>')[0]
            prices = price_text.split(' ')
            for price in prices:
                if 'Old' in price:
                    old_price = price.replace('Old:', '').replace('€', '').strip()
                if 'Price' in price:
                    new_price = price.replace('Price:', '').replace('€', '').strip()

        products.append({
            'link': product_link,
            'image': product_image,
            'name': product_name,
            'description': product_description,
            'new_price': new_price if new_price else 'null',
            'old_price': old_price if old_price else 'null'
        })

    return products
