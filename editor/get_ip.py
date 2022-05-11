from urllib.request import urlopen
import server

def public_ipv4():
    try:
        with urlopen('https://v4.tnedi.me') as response:
            return response.read().decode('ascii')
    except:
        with urlopen('https://v4.ident.me') as response:
            return response.read().decode('ascii')

url = f'{public_ipv4()}:{server.PORT}/index.html'

print(url)