


def get_cart_sum(order_positions):
    # order_positions[{"product":product, "count":count},{"product":product, "count":count}]
    # token promocode string
    sum = 0
    for e in order_positions:
        product = e['product']
        count = e['count']
        sum += product.price * count

    return sum


