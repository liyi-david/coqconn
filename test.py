#!python3
from coqconn.conn import CoqConnection
from coqconn.client import CoqClient

conn = CoqConnection.connect(timeout=20)
print(conn)

client = CoqClient(timeout=20)
print(client)

print(client.add('Definition a := 1'))

