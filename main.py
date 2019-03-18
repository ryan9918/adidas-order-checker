import requests
from bs4 import BeautifulSoup as bs
import json


class Checker():

	def __init__(self, locale):
		with open('locales.json') as file:
			locale_data = json.load(file)
			file.close()
		region = next(filter(lambda x: x['region'] == locale, locale_data['regions']), None)
		self.domain = region['domain']
		self.endpoint = region['endpoint']
		self.command = region['command']
		self.step1 = region['step1']
		self.step2 = region['step2']
		self.step3 = region['step3']
		self.step4 = region['step4']
		self.step5 = region['step5']
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
			'Origin': 'http://www.adidas{}'.format(region['domain'])
		}

	def check_order(self, order):
		number = order.split(':')[0]
		email = order.split(':')[1]
		s = requests.Session()
		r = s.get('https://www.adidas{}{}'.format(self.domain, self.endpoint), headers=self.headers)
		soup = bs(r.content, "html.parser")
		url = soup.find('form', {'id': 'dwfrm_ordersignup'})['action']
		data = {
			'dwfrm_ordersignup_orderNo': number,
			'dwfrm_ordersignup_email': email,
			'dwfrm_ordersignup_signup': self.command
		}
		r = s.post(url, data=data, headers=self.headers)
		soup = bs(r.content, "html.parser")
		try:
			items = soup.find_all('div', {'class': 'order-step selected'})
			for item in items:
				status = item.find('div', {'class': 'order-step-content-wrp'})
				status = status.text.strip()
			if str(status) == self.step1:
				print("Order {} for {} has not been confirmed yet and is still processing.".format(number, email))
				return False, False
			elif str(status) == self.step2:
				print("Order {} for {} is confirmed and waiting to be packed.".format(number, email))
				return True, False
			elif str(status) == self.step3:
				print("Order {} for {} is being prepared for shipping.".format(number, email))
				return True, False
			elif self.step4 in str(status):
				print("Order {} for {} has been shipped and is on its way to you!".format(number, email))
				return True, True
			elif str(status) == self.step5:
				print("Order {} for {} has been delivered!".format(number, email))
				return True, True
			else:
				return None, None
		except:
			print("Order {} for {} is an invalid input.".format(number, email))
			return None, None

	def read_orders(self, file):
		orders = []
		for item in file.read().splitlines():
			if not item == '':
				orders.append(item)
		return orders


if __name__ == '__main__':
	orders_dict = {
		'confirmed': [],
		'shipped': []
	}
	print("Adidas Order Checker V2")
	print("***************************************************************")
	print("@CrepChef")
	print("***************************************************************")
	locale = input("Enter locale (us/gb/fr/de): ").lower()
	print("")
	checker = Checker(locale)
	f = open('orders.txt', 'r')
	orders = checker.read_orders(f)
	f.close()
	for order in orders:
		confirmed, shipped = checker.check_order(order)
		if confirmed:
			orders_dict['confirmed'].append(order)
		if shipped:
			orders_dict['shipped'].append(order)
	print('\n\nYou have {} confirmed orders!'.format(len(orders_dict['confirmed'])))
	print('You have {} confirmed orders that have shipped!'.format(len(orders_dict['shipped'])))
	input('\nPress to exit.')