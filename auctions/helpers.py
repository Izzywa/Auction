from django.db.models import Max

def get_max_bid(listing):
    max = listing.bid.all().aggregate(Max("bid"))
    if max["bid__max"] != None:
        return max['bid__max']
    else:
        return listing.starting_bid

def watchlisted_user(listing):
    user_list = []
    for list in listing.watchlist.all():
        user_list.append(list.user)
    return user_list

def max_bidder(listing):
    return listing.bid.all().order_by('bid').last