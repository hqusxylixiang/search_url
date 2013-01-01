import re

def openConfig():
    f = open('config.conf')
    f.seek(0)
    config = []
    count = 0
    for line in f:
        c = re.split(',', line)
        config.append({
        	'id': count,
            'ip_diskstation': c[0],
            'port': c[1],
            'usuario': c[2],
            'password': c[3]
            })
       	count += 1
    f.close()
    return config


print openConfig()
