"""
Run Birdeye Client
"""
from birdeye import BirdEyeClient
from vars.constants import SOL_MINT
from custom_exceptions import InvalidTokens

# Initialize client
birdeye_client = BirdEyeClient()

token_address = SOL_MINT


# fetch Token Overview
# Currently giving InvalidToken error Birdeye API not working
try:
    token_overview = birdeye_client.fetch_token_overview(address=token_address)
    print("Token Overview: ", token_overview)
except InvalidTokens as err:
    print("Invalid Token error")

token_address_list = [
    SOL_MINT
]

# Fetch Prices Dex
prices_dex = birdeye_client.fetch_prices(token_addresses=token_address_list)

print("Birdeye Prices: ", prices_dex)
