import time
class Cache:
    def __init__(self, age):
        self.age = age
        self.store = {}

    def get(self, key):
        if key in self.store:
            v = self.store[key]
            exp = v['expiry']
            now = time.time()
            if(now < exp):
                return v['data']
            else:
                self.store.pop(key)
        return None

    def put(self, key, data):
        exp = time.time() + self.age
        self.store[key] = {
          'expiry' : exp,
          'data' : data
        }
