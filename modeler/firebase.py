import pandas as pd
import firebase_admin, uuid
from io import StringIO
from functools import wraps
from firebase_admin import initialize_app, credentials, firestore, storage

##################################### WRAPPERS ##################################################
def check_exists(func):
    @wraps(func)
    def wrapper(self, uri, **kwargs):
        if 'storage_files' not in dir(self):
            self.storage_files = self._list_files()
        self.file_exists = uri in self.storage_files
        return func(self, uri, **kwargs)
    return wrapper

def infer(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if func.__name__ in ['get','delete']:
            self.method = 'blob' if type(args[0]) == list or len(args[0].split('/')) > 1 else ('collection' if len(args) == 1 else 'document')
        if func.__name__ == 'post':
            self.method = 'blob' if len(args) == 2 else 'document'
        if func.__name__ == 'update':
            self.method = 'document'
        return func(self, *args, **kwargs)
    return wrapper

class Firebase:
    def __init__(self):
        self.app = initialize_app(credentials.Certificate('firebase_auth.json'),{'storageBucket':'trader-3870e.appspot.com'},str(uuid.uuid4()))
        self.fb = firestore.client(app=self.app)
        self.bucket = storage.bucket(app=self.app)
    
    @infer
    def post(self, *args, **kwargs):
        return getattr(self, 'post_%s' % getattr(self, 'method'))(*args, **kwargs)

    @infer
    def get(self, *args, **kwargs):
        return getattr(self, 'get_%s' % getattr(self, 'method'))(*args, **kwargs)

    @infer
    def update(self, *args, **kwargs):
        return getattr(self, 'update_%s' % getattr(self, 'method'))(*args, **kwargs)

    @infer
    def delete(self, *args, **kwargs):
        return getattr(self, 'delete_%s' % getattr(self, 'method'))(*args, **kwargs)

    def get_blob(self, *args, **kwargs):
        if type(args[0]) == list:
            return [{uri: self._download_to_df(uri) if not kwargs.get('to_file') else self._download_to_file(uri, kwargs.get('root','downloads'))} for uri in args[0]]
        return self._download_to_df(args[0]) if not kwargs.get('to_file') else self._download_to_file(args[0], kwargs.get('root','downloads'))
    
    def get_document(self, *args, **kwargs):
        return self.fb.collection(args[0]).document(args[1]).get().to_dict()

    def get_collection(self, *args, **kwargs):
        return {doc.id: doc.to_dict() for doc in (self.fb.collection(args[0]).stream() if not kwargs else self.fb.collection(args[0]).where(kwargs['value'], kwargs['operator'], kwargs['condition']).stream())}

    def post_blob(self, *args, **kwargs):
        return self._upload_from_file(args[0], args[1]) if type(args[1]) == str else self._upload_from_df(args[0], args[1])

    def post_document(self, *args, **kwargs):
        self.fb.collection(args[0]).document(args[1]).set(args[2])

    def delete_blob(self, *args, **kwargs):
        if type(args[0]) == list:
            for uri in args[0]: self.bucket.blob(uri).delete()
        else:
            self.bucket.blob(args[0]).delete()

    def delete_document(self, *args, **kwargs):
        for doc in self.fb.collection(args[0]).stream():
            if doc.id in [args[1]] if type(args[1]) == str else args[1]: doc.reference.delete()

    def delete_collection(self, *args, **kwargs):
        for doc in self.fb.collection(args[0]).stream() if kwargs else self.fb.collection(args[0]).where(kwargs['value'], kwargs['operator'], kwargs['condition']).stream():
            doc.reference.delete()

    def update_document(self, *args, **kwargs):
        self.fb.collection(args[0]).document(args[1]).update(args[2])

    def _upload_from_file(self, uri, df):
        self.bucket.blob(uri).upload_from_filename(df)

    def _upload_from_df(self, uri, df):
        self.bucket.blob(uri).upload_from_string(df.to_csv(index=False), content_type='application/vnd.ms-excel')
    
    @check_exists
    def _download_to_df(self, uri):
        return False if not self.file_exists else pd.read_csv(StringIO(self.bucket.blob(uri).download_as_string().decode()), usecols=lambda x: x not in ['Unnamed: 0'])

    @check_exists
    def _download_to_file(self, uri, root='downloads'):
        self.bucket.blob(uri).download_to_filename('/'.join([root,uri.split('/')[-1]]))
        return False if not self.file_exists else '/'.join([root,uri.split('/')[-1]])

    def _list_files(self, directory=None):
        return [b.name for b in self.bucket.list_blobs()] if directory == None else ([b.name for b in self.bucket.list_blobs() if b.name.split('/')[0] == directory])
