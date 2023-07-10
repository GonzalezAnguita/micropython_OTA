## About miota

This project started as a fork from <a href="https://github.com/turfptax/ugit">UGIT project from Turfptax</a> but I decided to made a deep refactor to remove the network dependency and git dependencies. MIOTA works virtually the same but is more flexible allowing you to decide the network source and also where to fetch your files. 

## I want to see code first

```python
# boot.py

from miota import update

def doc_url_generator(tree_doc):
  return f'https://raw.githubusercontent.com/turfptax/ugit_test/main/{tree_doc["path"]}'

CONFIG = {
  'tree_url': 'https://api.github.com/repos/turfptax/ugit_test/git/trees/main?recursive=1',
  'headers': {
    'User-Agent': 'micropython-ota'
  },
  'doc_url_generator': doc_url_generator,
  'local_doc_ignore': ['/miota.py']
}

update(CONFIG)
```

The above example will download the Turfptax sample repository into your device. For a fully functional example you need to connect to WIFI first. You can see a fully functional example in the `sample` folder

### Installation

Simply put: copy miota.py onto the micropython board.
