# core/routes/api_crypto.py

from flask import Blueprint, jsonify
from core.utils.external import get_crypto_data_from_cmc

api_crypto = Blueprint('api_crypto', __name__)

@api_crypto.route('/api/cryptos')
def get_cryptos():
    cryptos = get_crypto_data_from_cmc()
    return jsonify(cryptos)
