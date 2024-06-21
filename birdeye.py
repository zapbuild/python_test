from decimal import Decimal

import requests

from utils.helpers import is_solana_address
from vars import constants
from common import (
    PriceInfo, TokenOverview, Pair, TokenInfo, TransactionData,
    Txns, Volume, PriceChange, Liquidity,
    Info, Website, Social
)
from custom_exceptions import NoPositionsError, InvalidSolanaAddress, InvalidTokens


class BirdEyeClient:
    """
    Handler class to assist with all calls to BirdEye API
    """

    @property
    def _headers(self):
        return {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": constants.BIRD_EYE_TOKEN,
        }

    def _make_api_call(self, method: str, query_url: str, *args, **kwargs) -> requests.Response:
        match method.upper():
            case "GET":
                query_method = requests.get
            case "POST":
                query_method = requests.post
            case _:
                raise ValueError(f'Unrecognised method "{method}" passed for query - {query_url}')
        resp = query_method(query_url, *args, headers=self._headers, **kwargs)

        self._validate_response(resp)
        return resp.json()

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

    def fetch_prices(self, token_addresses: list[str]) -> dict[str, dict[str, PriceInfo[Decimal, Decimal]]]:
        """
        For a list of tokens fetches their prices
        via multi-price API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[str, PriceInfo[Decimal, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity

        Raises:
            NoPositionsError: Raise if no tokens are provided
            InvalidToken: Raised if the API call was unsuccessful
        """
        token_prices = {}

        for token_address in token_addresses:
            # validating address token
            self._validate_token_address(token_address)

            response_data = self._make_api_call(
                "GET",
                query_url=constants.BIRD_EYE_PRICE_URL,
                params={"address": token_address}
            )
            data = response_data.get('data') or {}
            if data:
                value = data.get('value')
                update_human_time = data.get('updateHumanTime') or ''

                token_prices[token_address] = {
                    update_human_time: PriceInfo(value=value, liquidity=value)
                }

        return token_prices

    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via multi-price API ensuring each token has a price

        Args:
            address (str): A token address for which to fetch overview

        Returns:
            dict[str, float | str]: Overview with a lot of token information I don't understand

        Raises:
            InvalidSolanaAddress: Raise if invalid solana address is passed
            InvalidToken: Raised if the API call was unsuccessful
        """
        # validating address token
        self._validate_token_address(address)

        response = self._make_api_call(
            "GET",
            query_url=constants.BIRD_EYE_TOKEN_URL,
            params={"address": address}
        )

        token_data = response.get('data') or {}

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
