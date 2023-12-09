from django import template

register = template.Library()


@register.filter
def has_bid(user_bids, item_bids):
    return any(bid in user_bids for bid in item_bids)


@register.filter
def max_bid(user_bids, item):
    return max((bid.amount for bid in user_bids if bid.item == item))
