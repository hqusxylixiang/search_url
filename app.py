# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
from flask import request
from lib import url, html, synology, extension, links
import re
import base64
import os
app = Flask(__name__)

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
            'usuario': c[2]
            })
        count += 1
    f.close()
    return config


def openLine(line):
    f = open('config.conf')
    f.seek(int(line))
    l = f.readline()
    c = re.split(',', l)
    config = {
        'id': line,
        'ip_diskstation': c[0],
        'port': c[1],
        'usuario': c[2],
        'password': c[3]
    }
    f.close()
    return config


class run:
    def __init__(self, url_in, ext=[], forb=[]):
        try:
            self.url = url.url(url_in)
        except url.InvalidProtocol:
            return "Has introducido una URL Incorrecta"
        except url.URLError:
            return "La URL que has introducido no existe"
        self.extensions = extension.extension(ext)
        self.forbbiden = extension.extension(forb)

    def check(self):
        if self.url.isValidURL():
            url_content = self.url.returnUrlContent()
            allLinks = html.html(url_content)
            allLinks = allLinks.findLinks()
            validLinks = self.extensions.searchExtension(allLinks)
            print validLinks
            forb = self.forbbiden.getExtension()
            if forb:
                for f in forb:
                    if f in validLinks:
                        validLinks.remove(f)
            print 'QUITADOS LOS INCORRECTOS'
            validLinks = html.listOfExceptions().check(validLinks, self.url.getURL())
            print 'EXCEPCIONES'
            return validLinks


@app.route('/', methods=['GET'])
def home():
        t = 'index.html'
        return render_template(t)



@app.route('/enlaces', methods=['POST'])
def enlaces():
    if request.method == 'POST':
            form = request.form
            url = form['url']
            ext = form['ext']
            ext = re.split(',', ext)
            forb = form['forb']
            forb = re.split(',', forb)
            r = run(url, ext, forb)
            sy_conf = openConfig()
            result = r.check()
            t = 'respuesta.html'
            return render_template(t, resultado=result, synology=sy_conf)
            # return render_template(t)


@app.route('/enviar', methods=['POST', 'GET'])
def enviar():
    config = openLine(request.form['synology'])
    result = request.form['links']
    result = re.split('\n', result)
    url = 'http://' + str(config['ip_diskstation']) + ':' + str(config['port'])
    syno = synology.synology(url, config['usuario'], config['password'])
    toAdd = ''
    for download in result:
        download = download.replace('\r', '')
        toAdd += download + ', '
    t = 'resultado.html'
    if (syno.addDownload(toAdd)):
        resultado = u'Añadido'
    else:
        resultado = u'Algo a fallado'
    return render_template(t, resultado=resultado)

with app.test_request_context('/', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/'
    assert request.method == 'POST'

with app.test_request_context('/enlaces', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/enlaces'
    assert request.method == 'POST'

with app.test_request_context('/enviar', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/enviar'
    assert request.method == 'POST'


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
