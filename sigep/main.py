# -*- encoding: utf-8 -*-
import os
import xml.dom.minidom
import urllib2
from util import *

SANDBOX_URL = 'https://apphom.correios.com.br/SigepMasterJPA/AtendeClienteService/AtendeCliente?wsdl'
PRODUCTION_URL = 'https://apps.correios.com.br/SigepMasterJPA/AtendeClienteService/AtendeCliente?wsdl'


class BaseConnObject(object):
    template = ''
    tags = ['faultcode', 'faultstring']

    def __init__(self, sandbox=False):
        self.headers = {'Content-Type': 'application/soap+xml; charset=iso-8859-1'}
        self.url = SANDBOX_URL if sandbox else PRODUCTION_URL


class SigepException(Exception):
    def __init__(self, id, message=None):
        self.id = id
        self.message = message

    def __str__(self):
        return u'%s - %s' % (self.id, self.message)


class ConsultaCEP(BaseConnObject):
    template = 'templates/consultaCEP.xml'

    def __init__(self, cep, sandbox=False):
        super(ConsultaCEP, self).__init__(sandbox=sandbox)
        self.cep = clean_postcode(cep)
        self.tags += ['bairro', 'cep', 'cidade', 'complemento', 'complemento2', 'end', 'id', 'uf']

    def do(self):
        self.documento = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.template), 'r').read() % self.__dict__
        self.requisicao = urllib2.Request(self.url, self.documento, self.headers)
        self.resposta = urllib2.urlopen(self.requisicao)
        self.conteudo = iso_2_utf(self.resposta.read())

        self.dom = xml.dom.minidom.parseString(self.conteudo)

        dados = {}

        for tag in self.tags:
            try:
                cont = self.dom.getElementsByTagName(tag)[0].childNodes[0].data
                dados[tag] = cont
            except IndexError:
                pass

        if dados.get('faultcode'):
            raise SigepException(dados.get('faultcode'), dados.get('faultstring', ''))

        return dados