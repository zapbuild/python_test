"""
Client for DexScreener APIs
"""
from decimal import Decimal
from typing import Any

import requests

from common import (
    PriceInfo, TokenOverview, Pair, TokenInfo, TransactionData,
    Txns, Volume, PriceChange, Liquidity,
    Info, Website, Social
)
from custom_exceptions import InvalidSolanaAddress, InvalidTokens, NoPositionsError
from utils.helpers import is_solana_address
from vars.constants import (
    SOL_MINT, DEX_TOKEN_URL, DEX_BULK_TOKEN_URL
)


class DexScreenerClient:
    """
    Handler class to assist with all calls to DexScreener API
    """

    @staticmethod
    def _validate_token_address(token_address: str):
        """
        Validates token address to be a valid solana address

        Args:
            token_address (str): Token address to validate

        Returns:
            None: If token address is valid

        Raises:
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """
        if not token_address:
            raise NoPositionsError("Token address is empty.")

        if not is_solana_address(token_address):
            raise InvalidSolanaAddress("Invalid Solana address: %s" % token_address)

    def _validate_token_addresses(self, token_addresses: list[str]):
        """
        Validates token addresses to be a valid solana address

        Args:
            token_addresses (list[str]): Token addresses to validate

        Returns:
            None: If token addresses are valid

        Raises:
            NoPositionsError: If token addresses are empty
            InvalidSolanaAddress: If any token address is not a valid solana address
        """
        if not token_addresses:
            raise NoPositionsError("Token addresses are empty.")

        for token_address in token_addresses:
            self._validate_token_address(token_address)

    @staticmethod
    def _validate_response(resp: requests.Response):
        """
        Validates response from API to be 200

        Args:
            resp (requests.Response): Response from API

        Returns:
            None: If response is 200

        Raises:
            InvalidTokens: If response is not 200
        """
        if resp.status_code != 200:
            raise InvalidTokens()

    def _call_api(self, token_address: str) -> dict[str, Any]:
        """
        Calls DexScreener API for a single token

        Args:
            token_address (str): Token address for which to fetch data

        Returns:
            dict[str, Any]: JSON response from API

        Raises:
            InvalidTokens: If response is not 200
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """
        self._validate_token_address(token_address)

        url = "%s%s" % (DEX_TOKEN_URL, token_address)
        response = requests.get(url)
        self._validate_response(response)

        return response.json()

    def _call_api_bulk(self, token_addresses: list[str]) -> dict[str, Any]:
        """
        Calls DexScreener API for multiple tokens

        Args:
            token_addresses (list[str]): Token addresses for which to fetch data

        Returns:
            dict[str, Any]: JSON response from API

        Raises:
            InvalidTokens: If response is not 200
            NoPositionsError: If token addresses are empty
            InvalidSolanaAddress: If any token address is not a valid solana address
        """
        self._validate_token_addresses(token_addresses)

        url = DEX_BULK_TOKEN_URL
        response = requests.post(url, json={"tokens": token_addresses})
        self._validate_response(response)

        return response.json()

    def fetch_prices_dex(self, token_addresses: list[str]) -> dict[str, dict[Decimal, PriceInfo[str, Decimal]]]:
        """
        For a list of tokens fetches their prices
        via multi API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[Decimal, PriceInfo[str, Decimal]]
           Mapping of token to a named tuple PriceInfo with price and liquidity in Decimal
        """
        token_prices = {}

        for token_address in token_addresses:
            token_overview = self._call_api(token_address=token_address)

            pairs = token_overview.get('pairs') or []
            max_entry = self.find_largest_pool_with_sol(token_pairs=pairs, address=token_address)
            if max_entry:
                liquidity_usd = Decimal(max_entry.get("liquidity", {}).get("usd", 0))
                liquidity_quote = Decimal(max_entry.get("liquidity", {}).get("quote", 0))
                liquidity_base = max_entry.get("dexId") or ""

                token_prices[token_address] = {
                    liquidity_quote: PriceInfo(value=str(liquidity_base), liquidity=liquidity_usd)
                }

        return token_prices

    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via Dex API ensuring each token has a price

        Args:
        address (str): A token address for which to fetch overview

        Returns:
        TokenOverview: Overview with a lot of token information I don't understand
        """
        token_data = self._call_api(address)

        pairs = []
        for pair in token_data.get('pairs') or []:
            pair_namedtuple = Pair(
                chainId=pair['chainId'],
                dexId=pair['dexId'],
                url=pair['url'],
                pairAddress=pair['pairAddress'],
                baseToken=TokenInfo(**pair['baseToken']),
                quoteToken=TokenInfo(**pair['quoteToken']),
                priceNative=pair['priceNative'],
                priceUsd=pair['priceUsd'],
                txns=TransactionData(
                    m5=Txns(**pair['txns']['m5']),
                    h1=Txns(**pair['txns']['h1']),
                    h6=Txns(**pair['txns']['h6']),
                    h24=Txns(**pair['txns']['h24'])
                ),
                volume=Volume(**pair['volume']),
                priceChange=PriceChange(**pair['priceChange']),
                liquidity=Liquidity(**pair['liquidity']),
                fdv=pair['fdv'],
                pairCreatedAt=pair['pairCreatedAt'],
                info=Info(
                    imageUrl=pair['info']['imageUrl'],
                    websites=[Website(**website) for website in pair['info']['websites']],
                    socials=[Social(**social) for social in pair['info']['socials']]
                )
            )
            pairs.append(pair_namedtuple)

        return TokenOverview(
            schemaVersion=token_data['schemaVersion'],
            pairs=pairs
        )

    @staticmethod
    def find_largest_pool_with_sol(token_pairs, address):
        max_entry = {}
        max_liquidity_usd = -1

        for entry in token_pairs:
            # Check if the baseToken address matches the specified address
            if entry.get("baseToken", {}).get("address") == address and entry["quoteToken"]["address"] == SOL_MINT:
                liquidity_usd = float(entry.get("liquidity", {}).get("usd", 0))
                if liquidity_usd > max_liquidity_usd:
                    max_liquidity_usd = liquidity_usd
                    max_entry = entry
        return max_entry
