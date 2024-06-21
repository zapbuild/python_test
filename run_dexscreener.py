"""
Run Dex Screener Client
"""
from dexscreener import DexScreenerClient

# Initialize client
dex_client = DexScreenerClient()

token_address = 'WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC'


# fetch Token Overview
token_overview = dex_client.fetch_token_overview(address=token_address)
print("Token Overview: ", token_overview)

token_address_list = [
    'WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC',
    '2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj',
    'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
    '2LxZrcJJhzcAju1FBHuGvw929EVkX7R7Q8yA2cdp8q7b'
]

# Fetch Prices Dex
prices_dex = dex_client.fetch_prices_dex(token_addresses=token_address_list)

print("Prices Dex: ", prices_dex)
