from typing import Dict

# Simple mock exchange rates. In production, fetch from an API (e.g. OpenExchangeRates)
EXCHANGE_RATES = {
    "USD": 1.0,
    "VND": 25500.0,
    "EUR": 0.92
}

CURRENCY_SYMBOLS = {
    "USD": "$",
    "VND": "₫",
    "EUR": "€"
}

class LocalizationService:
    @staticmethod
    def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return amount
        
        rate_from = EXCHANGE_RATES.get(from_currency, 1.0)
        rate_to = EXCHANGE_RATES.get(to_currency, 1.0)
        
        # Convert to USD first
        amount_usd = amount / rate_from
        # Convert to target
        return amount_usd * rate_to

    @staticmethod
    def format_currency(amount: float, currency: str) -> str:
        symbol = CURRENCY_SYMBOLS.get(currency, currency)
        if currency == "VND":
             return f"{symbol}{amount:,.0f}" # VND usually no decimals
        return f"{symbol}{amount:,.2f}"
