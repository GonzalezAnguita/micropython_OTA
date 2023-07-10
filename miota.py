import os
import urequests as requests
import json
import hashlib
import binascii

# Utils
def is_directory(file_path):
  try:
    return os.stat(file_path)[8] == 0
  except:
    return False

def is_file(file_path):
  try:
    return os.stat(file_path)[8] != 0
  except:
    return False

def get_size(file_path):
  file = open(file_path)
  size = 0
  byte = file.read(1)
  while byte:
    size += 1
    byte = file.read(1)
  file.close()
  return size

def join_paths(*paths):
  final_path = ''
  for path in paths:
    if path.startswith('/') or final_path.endswith('/'):
      final_path += path
    else:
      final_path += f'/{path}'
  return final_path

def get_config_key(key, config, default=None):
  try:
    return config[key]
  except KeyError:
    if default is not None:
      return default
    raise Exception(f'Missing "{key}" in config')


def fetch_remote_doc(doc_url, headers, doc_path, required):
  res = requests.get(doc_url, headers=headers)

  new_file = open(doc_path, 'w')

  try:
    new_file.write(res.content.decode('utf-8'))
  except:
    if required:
      raise Exception(f'Could not fetch document {doc_path} marked as required')

  try:
    new_file.close()
  except:
    pass
  
def fetch_remote_doc_tree(url, headers):
  res = requests.get(url, headers=headers)

  try:
    data = json.loads(res.content.decode('utf-8'))
  except:
    raise Exception(f'Your document tree from {url} appears to be corrupted') 

  if 'tree' not in data:
    raise Exception(f'Corrupted document tree, expected "tree" to be a key inside {data}') 

  return data['tree']

def get_doc_sha(file_path):
  sha1 = hashlib.sha1()
  file = open(file_path)

  size = get_size(file_path)
  sha1.update(f'blob {size}\0')

  byte = file.read(1)
  while byte:
    sha1.update(byte)
    byte = file.read(1)

  digest = sha1.digest()
  return binascii.hexlify(digest).decode('utf-8')

def add_to_tree(file, prev_path, local_doc_tree, doc_ignore):
  file_path = join_paths(prev_path, file)

  if file_path in doc_ignore:
    return

  if is_directory(file_path):
    try:
      dir_files = os.listdir(file_path)
  
      if len(dir_files) == 0:
        return
  
      for path_file in dir_files:
        add_to_tree(
          file=path_file,
          local_doc_tree=local_doc_tree,
          prev_path=file_path
        )
    except:
      return

  else:
    try:
      file_hash = get_doc_sha(file_path=file_path)
      local_doc_tree.append({
        'path': file_path,
        'sha': file_hash
      })
    except Exception as e:
      print(e)
      raise Exception(f'Could not add document {file_path} to local tree')

def fetch_local_doc_tree(doc_ignore, basedir):
  local_doc_tree = []

  for path_file in os.listdir(basedir):
    add_to_tree(
      file=path_file,
      prev_path=basedir,
      local_doc_tree=local_doc_tree,
      doc_ignore=doc_ignore
    )

  return local_doc_tree

def is_doc_in_tree(doc_sha, tree):
  for doc in tree:
    if doc['sha'] == doc_sha:
      return True
  return False

def update(config):
  default_headers = get_config_key(key='headers', config=config, default={})

  tree_url = get_config_key(key='tree_url', config=config)
  tree_headers = get_config_key(key='tree_headers', config=config, default=default_headers)

  remote_doc_tree = fetch_remote_doc_tree(url=tree_url, headers=tree_headers)

  for tree_doc in remote_doc_tree:
    file_type = tree_doc['type']
    file_path = tree_doc['path']
    
    if file_type == 'tree':
      if is_directory(file_path):
        continue
      os.mkdir(file_path)

    elif file_type == 'blob':
      if is_file(file_path):
        os.remove(file_path)
    
      doc_url_generator = get_config_key(key='doc_url_generator', config=config)
      doc_headers = get_config_key(key='doc_headers', config=config, default=default_headers)

      fetch_remote_doc(
        doc_url=doc_url_generator(tree_doc),
        headers=doc_headers,
        doc_path=file_path,
        required=True
      )
    else:
      print(f'Invalid file type "{file_type}" provided')

  local_doc_ignore = get_config_key(key='local_doc_ignore', config=config, default=[])
  local_doc_basedir = get_config_key(key='local_doc_basedir', config=config, default='/')

  local_doc_tree = fetch_local_doc_tree(doc_ignore=local_doc_ignore, basedir=local_doc_basedir)

  for local_doc in local_doc_tree:
    if is_doc_in_tree(doc_sha=local_doc['sha'], tree=remote_doc_tree):
      continue

    os.remove(local_doc['path'])
