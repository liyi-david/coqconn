#!python3
from coqconn.conn import CoqConnection
from coqconn.client import CoqClient

client = CoqClient(timeout=20)

print(client.add('Definition a := 1.'))
print(client.add('Definition a := 1'))
print(client.add('Definition b := a.'))

