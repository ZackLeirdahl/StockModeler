from ..firebase import Firebase

def get(uri):
    return Firebase().get(uri)

def post(data):
    if 'df' in data.keys():
        Firebase().post(data['uri'], data['df'])
    else:
        Firebase().post(data['collection'], data['key'], data['data'])