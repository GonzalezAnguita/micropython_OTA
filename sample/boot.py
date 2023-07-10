import network
import machine
import time

from miota import update

WIFI_SSID = 'YOUR-SSID'
WIFI_PASSWORD = 'YOUR-PASSWORD'

# Connect to wifi

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Connecting to network...')
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        pass

    print('Connection successful')
    print('Network config:', wlan.ifconfig())


def doc_url_generator(tree_doc):
  file_path = tree_doc['path']

  return f'https://raw.githubusercontent.com/turfptax/ugit_test/main/{file_path}'

CONFIG = {
  'tree_url': 'https://api.github.com/repos/turfptax/ugit_test/git/trees/main?recursive=1',
  'headers': {
    'User-Agent': 'micropython-ota'
    # 'Authorization': f'bearer {AUTH_TOKEN}' 
  },
  # 'tree_headers': {
  #   'User-Agent': 'micropython-ota',
  #   'Authorization': f'bearer {AUTH_TOKEN}' 
  # },
  # 'doc_headers': {
  #   'User-Agent': 'micropython-ota',
  #   'Authorization': f'bearer {AUTH_TOKEN}' 
  # },
  'doc_url_generator': doc_url_generator,
  'local_doc_ignore': ['/miota.py'],
  'local_doc_basedir': '/'
}

update(CONFIG)

print('Resetting machine in 10')
time.sleep(10)

machine.reset()
