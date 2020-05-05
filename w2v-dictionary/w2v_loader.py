# Load all embeddings from http://vectors.nlpl.eu/

import os
from tqdm import tqdm
import requests
import time
import zipfile
import tempfile


EMBEDDING_URL = "http://vectors.nlpl.eu/repository/20/200.zip"

CACHE_DIR = "~/.cache/w2v"
CACHE_DIR = os.path.expanduser(CACHE_DIR)

EMBEDDING_FILE = "model.txt"

def download_file(data_url, output_file):
    with requests.get(data_url, stream=True) as resp:

        size = int(resp.headers["Content-Length"])
        print(f"Loading {size} bytes from {data_url}")

        block_size = 1024 # 1 kiB

        with tqdm(total=size, unit="iB", unit_scale=True) as prog:

            start = time.time()
            for block in resp.iter_content(block_size):
                prog.update(len(block))
                output_file.write(block)

            took = time.time() - start

        print(f"Loaded {size} compressed bytes in {took:.4} seconds")


def extract_file(zip_path, output_file, file_to_extract):
    extracting = zipfile.ZipFile(zip_path)

    size = extracting.getinfo(file_to_extract).file_size
    print(f"Extracting {size} bytes")

    buf = extracting.open(file_to_extract)

    block_size = 1024

    with tqdm(total=size, unit="iB", unit_scale=True) as prog:
        start = time.time()
        while True:
            read = buf.read(block_size)
            prog.update(len(read))

            if len(read) == 0:
                break
            output_file.write(read)

        took = time.time() - start

    print(f"Extracted {size} bytes in {took:.4} seconds")


def get_or_load_model(mode="rb"):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    emb_path = os.path.join(CACHE_DIR, EMBEDDING_FILE)
    if os.path.isfile(emb_path):
        return open(emb_path, mode)

    tmp_dir = tempfile.gettempdir()

    zip_loc = os.path.join(tmp_dir, "model.zip")

    download_file(EMBEDDING_URL, open(zip_loc, "wb"))

    extract_file(zip_loc, open(emb_path, "wb"), "model.txt")
    return open(emb_path, mode)


if __name__ == "__main__":
    get_or_load_model("r")

