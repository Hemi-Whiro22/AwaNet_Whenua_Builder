import chardet

with open('/workspaces/The_Awa_Network/te_po/.env', 'rb') as f:
    data = f.read()
    print(chardet.detect(data))