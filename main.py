import os
import requests
import json
import logging
import datetime
try:
    from elasticsearch_dsl import Index
    from elasticsearch import Elasticsearch, helpers
except ImportError:
    print("elasticsearch is not installed. Report to ELK will not be available")

TODAY = datetime.datetime.today().strftime('%Y-%m-%d')
LOG_FILE = "{}.log".format(TODAY)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
ELASTIC_HOST = os.environ.get('TMV1_ELASTIC_HOST')
token = os.environ.get('TMV1_TOKEN')
url_base = 'https://api.eu.xdr.trendmicro.com'
url_path = '/beta/xdr/datalake/dataPipelines'
query_params = {}
body = {
"type": "detection",
"description": "to siemhost2"
}
headers = {'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json;charset=utf-8'}

def timechange(string):
    tmp = string / 1000.0
    try:
        isotime = datetime.datetime.fromtimestamp( tmp )
        return isotime.isoformat()
    except Exception as e:
        today = datetime.datetime.now()
        iso_date = today.isoformat()
        return iso_date


def elk_report(name,data):
        # Elasticsearch report
        today = datetime.datetime.now()
        iso_date = today.isoformat()
        tmp = json.loads(data)
        timestamp = {"timestamp" : timechange(tmp["eventTime"])}
        
        result = tmp.update(timestamp)
        print(json.dumps(tmp, indent=4, sort_keys=False))
        source = json.dumps(data, indent=4, sort_keys=False)
        epoch_time = datetime.datetime.today().strftime('%Y-%m-%d')
        index_name = "{}-{}".format(name, str(epoch_time))

        #body = ({'timestamp' : datetime.datetime.now(),
        #        'report' : data
        #    })
        body = tmp
        try:
            es = Elasticsearch([{'host': ELASTIC_HOST, 'port': '9200'}])
            
            try:
                index = Index(index_name, es)
                index.settings(
                index={'mapping':{'ignore_malformed':True}}
                )
                index.create()
            except:
                pass
            es.index(index=index_name, doc_type='json', document=body)
            #helpers.bulk(es, body, index=index_name)
            logger.info("{} : message: [{}].".format(datetime.datetime.now(), es))
        except Exception as err:
            logger.error("{} : message: [Elastic: {}].".format(datetime.datetime.now(), err))
            pass


def index_data_to_es(es, docs):
    def index_actions(name, data):
        for source in data:
            yield {
                '_index': name,
                '_op_type': 'index',
                '_source': source
            }
    for name, data in docs.items():
        helpers.bulk(es, index_actions(name, data))



def GetPipelineInfo(id):
    url_path = '/beta/xdr/datalake/dataPipelines/{id}'
    url_path = url_path.format(**{'id': id})


    query_params = {}
    headers = {'Authorization': 'Bearer ' + token}

    r = requests.get(url_base + url_path, params=query_params, headers=headers)

    if 'application/json' in r.headers.get('Content-Type', '') and len(r.content):
        print(json.dumps(r.json(), indent=4))
    else:
        print(r.text)
    return


def ListPackages(id):

    url_path = '/beta/xdr/datalake/dataPipelines/{id}/packages'
    url_path = url_path.format(**{'id': id})

    end = datetime.datetime.now()
    start = end - datetime.timedelta(hours=1, minutes=10)    

    #query_params = {'top': '50'}
    query_params = {"startDateTime": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "top": 50}
    print(query_params)
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get(url_base + url_path, params=query_params, headers=headers)
    if 'application/json' in r.headers.get('Content-Type', '') and len(r.content):
        ret = r.json()
        try:
            for rr in ret["items"]:
                if "id" in rr:
                    GetPackages(id, rr["id"])
        except:
            print(r.json())
    else:
        print(r.text)

def GetPackages(id,packageId):
    url_path = '/beta/xdr/datalake/dataPipelines/{id}/packages/{packageId}'
    url_path = url_path.format(**{'id': id, 'packageId': packageId})
    query_params = {}
    logs =[] 
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get(url_base + url_path, params=query_params, headers=headers)
    if 'application/json' in r.headers.get('Content-Type', '') and len(r.content):
        print(json.dumps(r.json(), indent=4))
        elk_report("visionone-raw",r.json())
    else:
        try:
            print(json.dumps(r.json(), indent=4))
            elk_report("visionone-raw",r.json())
        except:
            for line in r.text.splitlines():
                elk_report("visionone-raw",line)
                #
                #logs.append(line)

        #print(json.dumps(logs, indent=4, sort_keys=True))
        #elk_report("visionone-raw",logs)


def run():
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get(url_base + url_path, params=query_params, headers=headers)
    if 'application/json' in r.headers.get('Content-Type', '') and len(r.content):
        ret = r.json()
        for rr in ret["items"]:
            ListPackages(rr["id"])
    else:
        print(r.text)



if __name__ == '__main__':
    run()