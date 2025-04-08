import hashlib

class MetricsData:

    def __init__(self):
        self.data_container = {}

    def create_keyed_data(self, category, key, data_to_set=None):
        if category not in self.data_container:
            self.data_container[category] = {}
        self.data_container[category][key] = {
                'data' : data_to_set if data_to_set is not None else {},
                'used' : False
            }


    @staticmethod
    def encode_user(username):
        hashed_username = hashlib.blake2b(username.encode(), digest_size=12).hexdigest()
        return hashed_username


    def get_data(self, category, key=None):
        
        if category in self.data_container:
            if key is not None:
                if key in self.data_container[category]:
                    self.data_container[category][key]['used'] = True
                    return self.data_container[category][key]['data']
                else:
                    raise Exception(f'key {key} not in data: {self.data_container[category].keys()}')
            else:
                return self.data_container[category]
        else:
            raise Exception(f'Category {category} not in data: {self.data_container.keys()}')

        

    def set_data(self, category, key, data):
        if not (category in self.data_container and key in self.data_container[category]):
            self.create_keyed_data(category, key, data)
        else:
            self.data_container[category][key]['data'] = data

    def all_used(self):
        are_all_used = True
        for category in self.data_container:
            for key in self.data_container[category]:
                if 'used' in self.data_container[category][key] and not self.data_container[category][key]['used']:
                    print(f'Key {key} in category {category} not used')
                    are_all_used = False
        return are_all_used

