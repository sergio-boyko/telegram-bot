############################################################
# Бот для получения курсов валят с помощью API приватбанка #
# автор: Бойко Сергей                                      #
# дата: 06.01.2019                                         #
# почта: sergio.boyko.work@gmail.com                       #
############################################################
import requests
import re
import json
from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

URL_API_BANK = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'
URL_API_TELEGRAM = 'https://api.telegram.org/bot690622649:AAGXT672HS93vts9I3G73crJW0TF_Z3_tqw/'


@app.route('/', methods=['POST', 'GET'])
def index():
	if request.method == 'POST':
		r = request.get_json()
		chat_id = r['message']['chat']['id']
		message = r['message']['text']
		pattern = r'/usd|eur|rur|btc|all'

		if re.search(pattern, message):
			cur = parse_text(message)
			if cur == 'all':
				price = get_all_cur()
			else:
				price = get_cur(str.upper(parse_text(message)))

			send_message(chat_id, text=price)

			return jsonify(r)
		else:
			cmd = 'Доступные команды:\n/usd - Узнать курс валют Доллара к гривне\n/eur - Узнать курс валют Евро к гривне\n/rur - Узнать курс валют Рубля к гривне\n/btc - Узнать курс валют Биткоина к гривне\n/all - Узнать все курсы'

			send_message(chat_id, text=cmd)
			return jsonify(r)
	return '<h1>PrivatBankBot</h1>'


def parse_text(text):
    pattern = r'/\w+'
    crypto = re.search(pattern, text).group()

    return crypto[1:]


def get_response_bank():
    """ To get response from a bank """
    r = requests.get(URL_API_BANK)

    return r.json()


def get_cur(cur='USD'):
    json_r = get_response_bank()

    for i in json_r:
        if i['ccy'] == cur:
            price = f"{float(i['sale']):.{2}f}"

            return 'Курс гривны к {0}: {1} грн за 1 {0}'.format(cur, price)


def get_all_cur():
    json_r = get_response_bank()
    msg = ''
    for i in json_r:
        price = f"{float(i['sale']):.{2}f}"
        msg += 'Курс гривны к {0}: {1} грн за 1 {0}\n'.format(i['ccy'], price)

    return msg


def send_message(chat_id, text='KYS'):
    _url = URL_API_TELEGRAM + 'sendMessage'
    answer = {
        'chat_id': chat_id,
        'text': text
    }
    r = requests.post(_url, json=answer)

    return r.json()


if __name__ == '__main__':
	app.run(debug=True)
