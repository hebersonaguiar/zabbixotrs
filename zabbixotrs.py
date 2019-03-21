#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Out 22 10:57:32 2018

@author: Heberson Aguiar <heberson.aguiar@hepta.com.br>
"""

from zabbix_api import ZabbixAPI
from pyotrs import Client, Article, Ticket, DynamicField
from mysql.connector import Error
import mysql.connector
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

ZBX_SERVER     = "http://x.x.x.x/zabbix"
ZBX_USER       = sys.argv[1]
ZBX_PASS       = sys.argv[2] 
OTRS_SERVER    = "http://x.x.x.x"
OTRS_USER      = sys.argv[3]
OTRS_PASS      = sys.argv[4]
OTRS_DB_NAME   = "otrs"
OTRS_DB_USER   = sys.argv[5]
OTRS_DB_PASS   = sys.argv[6]
OTRS_DB_SERVER = "x.x.x.x"
QUEUE 	       = "9 - Gestão de Liberação::Infraestrutura"
STATE 	       = "Registrada"
PRIORITY       = "3 normal"
CUSTOMERUSER   = "heberson.aguiar"
SERVICE        = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.2 - Servidores virtuais::2.2.2.1 - Investigar"
SLA            = "2 - Sustentação::0::NA"
TYPE           = "Problema"


def getTriggers(ZBX_SERVER, ZBX_USER, ZBX_PASS):

	zapi = ZabbixAPI(server=ZBX_SERVER)
	zapi.login(ZBX_USER, ZBX_PASS)

	triggers = zapi.trigger.get ({
            "output": ["description", "lastchange", "triggerid", "priority"],
            "selectHosts": ["hostid", "host"],
            "selectLastEvent": ["eventid", "acknowledged", "objectid", "clock", "ns"],
            "sortfield" : "lastchange",
            "monitored": "true",
            "only_true": "true",
            "maintenance":  "false",
            "expandDescription": True,
            "filter":{"value":1}
            })

	triggerid = []

    	for y in triggers:
             nome_host = y["hosts"][0]["host"]
             severity = int(y["priority"])
             triggerid.append(y["triggerid"])
    
             idade = time.time() - float(y["lastchange"])
             pegadia = "{0.tm_yday}".format(time.gmtime(idade))
             dia = int(pegadia) - 1
             duracao = "dias {0.tm_hour} horas {0.tm_min} minutos".format(time.gmtime(idade))
             ultima_alteracao = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(float(y["lastchange"])))

    
        return triggerid

def getHostGroup(ZBX_SERVER, ZBX_USER, ZBX_PASS, HOST):

    zapi = ZabbixAPI(server=ZBX_SERVER)
    zapi.login(ZBX_USER, ZBX_PASS)

    hostinfo = zapi.host.get({"filter":{"host":HOST},"output":"hostid", "selectGroups": "extend", "selectParentTemplates": ["templateid","name"]})[0]

    host_group_list = []

    for x in hostinfo["groups"]:
        host_group_list.append(x["name"])
        hostgroup = str(host_group_list)
    
    return hostgroup


def getTriggersDB(OTRS_DB_NAME, OTRS_DB_USER, OTRS_DB_PASS, OTRS_DB_SERVER):

	connection = mysql.connector.connect(host=OTRS_DB_SERVER,
                         database=OTRS_DB_NAME,
                         user=OTRS_DB_USER,
                         password=OTRS_DB_PASS)

        query = "SELECT \
                TB2.value_text AS triggerid \
            FROM dynamic_field TB1 \
                INNER JOIN dynamic_field_value TB2 ON TB2.field_id = TB1.id \
                INNER JOIN ticket TB3 ON TB3.id = TB2.object_id \
            WHERE TB1.name = 'TriggerID' AND TB1.valid_id = 1 AND TB3.ticket_state_id = 12  AND TB2.value_text;"

        rows = []

        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
        	rows.append(row[0])

        return rows

def getTriggersAndTicketDB(OTRS_DB_NAME, OTRS_DB_USER, OTRS_DB_PASS, OTRS_DB_SERVER):

	connection = mysql.connector.connect(host=OTRS_DB_SERVER,
                         database=OTRS_DB_NAME,
                         user=OTRS_DB_USER,
                         password=OTRS_DB_PASS)

        query = "SELECT \
                TB2.value_text AS triggerid, \
                TB3.id AS ticketid \
            FROM dynamic_field TB1 \
                INNER JOIN dynamic_field_value TB2 ON TB2.field_id = TB1.id \
                INNER JOIN ticket TB3 ON TB3.id = TB2.object_id \
            WHERE TB1.name = 'TriggerID' AND TB1.valid_id = 1 AND TB3.ticket_state_id = 12  AND TB2.value_text;"

        rows = []

        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
        	rows.append(row[0])

        return rows

def buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE ,SLA, TYPE, HOSTGROUP):

	client = Client(OTRS_SERVER, OTRS_USER, OTRS_PASS)
	client.session_create()
	new_ticket = Ticket.create_basic(Title=""+ DESCRIPTION +"",
                             Queue="" +  QUEUE + "",
                             State=u"" +  STATE + "",
                             Priority=u"" +  PRIORITY + "",
                             SLA="" + SLA  + "",
                             Type="" +  TYPE  + "",
                             Service="" + SERVICE + "",
                             CustomerUser="" +  CUSTOMERUSER + "")
	first_article = Article({"Subject": "Server " + HOST + " Down"  , "Body": "Host: " + HOST + " Trigger ID: " + TRIGGERID +" Severity: " + SEVERITY + " HostGroup: " + HOSTGROUP + " Descricao: " + DESCRIPTION })
	dynamic_field = DynamicField("TriggerID", value="" + TRIGGERID + "")
	client.ticket_create(new_ticket, first_article, None ,dynamic_fields=[dynamic_field])

	return "Ticket Build"


def getHostGroupTrigger(HOST, TRIGGERID, SEVERITY, HOSTGROUP, DESCRIPTION):

	list_groups = getHostGroup(ZBX_SERVER, ZBX_USER, ZBX_PASS, HOST)
 	if 'ICS/CORREIO' in str(list_groups) or 'SS/MAIL' in str(list_groups) or 'SS/MAIL/SMTP' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.1- Itens organizacionais::2.1.2 - Caixas postais de correio eletrônico::2.1.2.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'SS/AUTHENTICATION/AD' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.1- Itens organizacionais::2.1.3 - Domínios (LDAP)::2.1.3.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'Virtualização' in str(list_groups) or 'ICS/SRV-FISICOS' in str(list_groups) or 'Virtualizacao::Vmware' in str(list_groups) or 'CLOUD/HYPERVISOR/VMWARE' in str(list_groups) or 'ICS/VIRTUALIZACAO' in str(list_groups) or 'CLOUD/BAREMETAL' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.1 - Servidores físicos::2.2.1.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'NETWORKS/ROUTER' in str(list_groups) or 'NETWORKS/ROUTER/EXTERNAL' in str(list_groups) or 'ICS/ROTEADORES' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.10 - Roteadores::2.2.10.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'ICS/LINKS-INTERNET' in str(list_groups) or 'URL/SSL' in str(list_groups) or 'URL/INTERNAL' in str(list_groups) or 'URL/EXTERNAL' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.11 - Links com a Internet::2.2.11.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'SECURITY' in str(list_groups) or 'ICS/FIREWALL' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.13 - Sistemas ou Hardwares de Segurança da Informação::2.2.13.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'ICS/ATIVOS-WIFI' in str(list_groups) or 'NETWORKS/ACCESS-POINT' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.14 -  Ativos ou Passivos de rede e WiFi::2.2.14.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'Voip' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.15 - Telefonia IP (apenas hardware)::2.2.15.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'ICS/SRV-VIRTUAIS' in str(list_groups) or 'CLOUD/VMS' in str(list_groups) or 'Maquinas Virtuais Srv085' in str(list_groups) or 'SO/LINUX' in str(list_groups) or 'SO/WINDOWS' in str(list_groups) or 'Windows servers' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.2 - Servidores virtuais::2.2.2.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'Storage' in str(list_groups) or 'ICS/STORAGES' in str(list_groups) or 'CLOUD/STORAGE' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.6 - Storages corporativos::2.2.6.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'CLOUD/BACKUP' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.7 - Sistema de backup::2.2.7.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'Switches' in str(list_groups) or 'NETWORKS/SWITCH/ACCESS' in str(list_groups) or 'NETWORKS/SWITCH/CORE' in str(list_groups) or 'NETWORKS/SWITCH/DISTRIBUTION' in str(list_groups) or 'ICS/GERENCIA-INFRA' in str(list_groups) or 'ICS/GERENCIA-SERVICOS' in str(list_groups) or 'ICS/SWITCHES' in str(list_groups) or 'Newave' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.2 - Itens de Hardware::2.2.8 - Switches::2.2.8.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'DATABASES/MSSQL' in str(list_groups) or 'DATABASES/MYSQL' in str(list_groups) or 'ICS/SGBD' in str(list_groups) or 'DATABASES' in str(list_groups) or 'DATABASES/SQLSERVER' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.3 - Itens de Software::2.3.1 - Gerenciador de banco de dados::2.3.1.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'ICS/CONTROLE-COD-MALICIOSOS' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.3 - Itens de Software::2.3.13 - Sistema centralizado de controle de código malicioso::2.3.13.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'SS/APPLICATION/APACHE' in str(list_groups) or 'SS/APPLICATION/HTTP' in str(list_groups) or 'SS/FTP' in str(list_groups) or 'Servidor de Arquivos' in str(list_groups) or 'ICS/SRV-SITES' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.3 - Itens de Software::2.3.2 - Servidor WEB (IIS, Apache, outros)::2.3.2.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'ZBX/MONITOR' in str(list_groups) or 'ZBX/SERVER' in str(list_groups) or 'ICS/MONITORAMENTO' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.3 - Itens de Software::2.3.6 - Sistema centralizado de monitoramento de infraestrutura de TI::2.3.6.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'ICS/SRV-SISTEMAS' in str(list_groups) or 'ICS/SISTEMAS' in str(list_groups) or 'Sistema' in str(list_groups) or 'SRV204::Websites' in str(list_groups) or 'SRV209::Websites' in str(list_groups) or 'SEI - PROD' in str(list_groups) or 'QlikView' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.4 - Serviços de TI Disponibilizados::2.4.1 - Sistemas aplicativos::2.4.1.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	elif 'ICS/SITES' in str(list_groups) or 'Websites' in str(list_groups) or 'Portal Homologacao' in str(list_groups) or 'Websites::Produção' in str(list_groups) or 'Portal Producao' in str(list_groups):
 		SERVICE = "Problema::2 - Sustentação::2.4 - Serviços de TI Disponibilizados::2.4.2 - Sites WEB (Internet, intranet e extranets)::2.4.2.1 - Investigar"
 		buildTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, HOST, TRIGGERID, SEVERITY, DESCRIPTION, QUEUE, STATE, PRIORITY, CUSTOMERUSER, SERVICE, SLA, TYPE, HOSTGROUP)
 	else:
 		print "NENHUM GRUPO ENCONTRADO"


def closeTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, ZBX_SERVER, ZBX_USER, ZBX_PASS):
	
	zapi = ZabbixAPI(server=ZBX_SERVER)
	zapi.login(ZBX_USER, ZBX_PASS)
	client = Client(OTRS_SERVER, OTRS_USER, OTRS_PASS)
	client.session_create()

	connection = mysql.connector.connect(host=OTRS_DB_SERVER,
	                     database=OTRS_DB_NAME,
	                     user=OTRS_DB_USER,
	                     password=OTRS_DB_PASS)

	query = "SELECT \
	        TB2.value_text AS triggerid, \
	        TB3.id AS ticketid \
	    FROM dynamic_field TB1 \
	        INNER JOIN dynamic_field_value TB2 ON TB2.field_id = TB1.id \
	        INNER JOIN ticket TB3 ON TB3.id = TB2.object_id \
	    WHERE TB1.name = 'TriggerID' AND TB1.valid_id = 1 AND TB3.ticket_state_id = 12  AND TB2.value_text;"

	cursor = connection.cursor()
	cursor.execute(query)
	result = cursor.fetchall()
	for row in result:
	    TRIGGERID = row[0]
	    TICKETID = str(row[1])
	    TICKETINT = int(row[1])

	    triggers = zapi.trigger.get ({
            "output": ["description", "lastchange", "triggerid", "priority", "status", "state"],
            "selectHosts": ["hostid", "host"],
            "selectLastEvent": ["eventid", "acknowledged", "objectid", "clock", "ns", "state"],
            "sortfield" : "priority",
            "sortorder": "DESC",
            "selectDependencies": True,
            "monitored": "true",
            "only_true": "true",
            "maintenance":  "false",
            "expandDescription": True,
            "skipDependent": "1",
            "filter":{
                "value":0,
                "triggerid": ""+ TRIGGERID +""}
        })

	    for x in triggers:
	        HOST = x["hosts"][0]["host"]
	        severity = int(x["priority"])
	        status = x["status"]
	        triggerid = x["triggerid"]
	        state = x["state"]

	        if TRIGGERID == 0 and TICKETINT == 0:
	            print "Nenhum chamado para ser fechado"
	        else:
	            # print "Chamado com Trigger ID: " + TRIGGERID + " Ticket ID: " + TICKETID + " Sera Fechado"
	            client = Client(OTRS_SERVER, OTRS_USER, OTRS_PASS)
	            client.session_create()
	            article = Article({"Subject": "Chamado Fechado"  , "Body": "Problema com Servidor "+ HOST +" e Trigger ID: "+ TRIGGERID +" resolvido!"})
	            client.ticket_update(TICKETINT, article, attachments=None, dynamic_fields=None, State=u"Concluido")



def createTicket(ZBX_SERVER, ZBX_USER, ZBX_PASS):
	triggerszabbix = getTriggers(ZBX_SERVER, ZBX_USER, ZBX_PASS)
	triggersotrs   = getTriggersDB(OTRS_DB_NAME, OTRS_DB_USER, OTRS_DB_PASS, OTRS_DB_SERVER)

	difftriggers = list(set(triggerszabbix) - set(triggersotrs))

	for TRIGGERID in difftriggers:
		if not TRIGGERID:
			print "Lista vazia"
		else:
			zapi = ZabbixAPI(server=ZBX_SERVER)
			zapi.login(ZBX_USER, ZBX_PASS)

			triggers = zapi.trigger.get ({
		            "output": ["description", "lastchange", "triggerid", "priority"],
		            "selectHosts": ["hostid", "host"],
		            "selectLastEvent": ["eventid", "acknowledged", "objectid", "clock", "ns"],
		            "sortfield" : "lastchange",
		            "selectGroups": ["groupid", "name"],
		            "monitored": "true",
		            "only_true": "true",
		            "maintenance":  "false",
		            "expandDescription": True,
		            "filter":{
		            	"value":1,
		            	"triggerid": ""+ TRIGGERID +""}
		            })

		    	for y in triggers:
		             HOST = y["hosts"][0]["host"]
		             severity = int(y["priority"])
		             TRIGGERID = y["triggerid"]
		             DESCRIPTION = y["description"]
		             HOSTGROUP = y["groups"][0]["name"]

		             if severity == 0:
		             	SEVERITY = "Not Classified"
		             elif severity == 1:
		             	SEVERITY = "Information"
		             elif severity == 2:
		             	SEVERITY = "Warning"
		             	getHostGroupTrigger(HOST, TRIGGERID, SEVERITY, HOSTGROUP, DESCRIPTION)
		             elif severity == 3:
		             	SEVERITY = "Average"
		             	getHostGroupTrigger(HOST, TRIGGERID, SEVERITY, HOSTGROUP, DESCRIPTION)
		             elif severity == 4:
		             	SEVERITY = "High"
		             	getHostGroupTrigger(HOST, TRIGGERID, SEVERITY, HOSTGROUP, DESCRIPTION)
		             elif severity == 5:	
		             	SEVERITY = "Disaster"
		             	getHostGroupTrigger(HOST, TRIGGERID, SEVERITY, HOSTGROUP, DESCRIPTION)
		             else:
		             	print "Unknown Severity"

	return "Chamado criado com sucesso!"

closeTicket(OTRS_SERVER, OTRS_USER, OTRS_PASS, ZBX_SERVER, ZBX_USER, ZBX_PASS)
createTicket(ZBX_SERVER, ZBX_USER, ZBX_PASS)
