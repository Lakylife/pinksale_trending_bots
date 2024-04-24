import requests

def open_website_with_proxy(url, proxy):
    try:
        response = requests.get(url, proxies=proxy)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Chyba při připojování k webu: {e}")
        return None

def get_current_ip():
    try:
        response = requests.get('https://api.ipify.org')
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Nepodařilo se získat IP adresu: {e}")
        return None
