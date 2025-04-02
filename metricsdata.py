import hashlib

class MetricsData:

    def __init__(self):
        self.data_container = {}

    def create_keyed_data(self, key, data_to_set=None):
        self.data_container[key] = {
                'data' : data_to_set if data_to_set is not None else {},
                'used' : False
            }


    @staticmethod
    def encode_user(username):
        hashed_username = hashlib.blake2b(username.encode(), digest_size=12).hexdigest()
        return hashed_username


    def get_data(self, key):
        # If the key exists we assume it is requested to be used
        # not to be set
        if key in self.data_container:
            self.data_container[key]['used'] = True
            return self.data_container[key]['data']
        else:
            raise Exception(f'Key {key} not in data: {self.data_container.keys()}')
            
        

    def set_data(self, key, data):
        # If the key exists we assume it is requested to be used
        # not to be set
        if not key in self.data_container:
            self.create_keyed_data(key, data)
        else:
            self.data_container[key]['data'] = data

    def all_used(self):
        are_all_used = True
        for key in self.data_container:
            if 'used' in self.data_container[key] and not self.data_container[key]['used']:
                print(f'Key {key} not used')
                are_all_used = False
        return are_all_used

