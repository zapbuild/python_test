from collections import namedtuple

PriceInfo = namedtuple("PriceInfo", ["value", "liquidity"])

TokenInfo = namedtuple('TokenInfo', ['address', 'name', 'symbol'])
Txns = namedtuple('Txns', ['buys', 'sells'])
TransactionData = namedtuple('TransactionData', ['m5', 'h1', 'h6', 'h24'])
Volume = namedtuple('Volume', ['h24', 'h6', 'h1', 'm5'])
PriceChange = namedtuple('PriceChange', ['m5', 'h1', 'h6', 'h24'])
Liquidity = namedtuple('Liquidity', ['usd', 'base', 'quote'])
Website = namedtuple('Website', ['label', 'url'])
Social = namedtuple('Social', ['type', 'url'])
Info = namedtuple('Info', ['imageUrl', 'websites', 'socials'])
Pair = namedtuple('Pair', [
    'chainId', 'dexId', 'url', 'pairAddress', 'baseToken', 'quoteToken',
    'priceNative', 'priceUsd', 'txns', 'volume', 'priceChange', 'liquidity',
    'fdv', 'pairCreatedAt', 'info'
])
TokenOverview = namedtuple('TokenOverview', ['schemaVersion', 'pairs'])
