import redis
import pickle

pool = redis.ConnectionPool(host='10.0.0.96', port=9736, password='ZGzjshzsjgqjfdl9@',decode_responses=True)
r = redis.Redis(connection_pool=pool)
r.set('food', 'mutton', ex=3)       # key是"food" value是"mutton" 将键值对存入redis缓存
print(r.get('food'))                # mutton 取出键food对应的值


class RedisCache:
    config = {
        'host'      : '10.0.0.96',
        'port'      : 9736,
        'password'  : 'ZGzjshzsjgqjfdl9@',
    }

    def start(self, host=None, port=None, password=None):
        if(host is not None): self.config['host'] = str(host) # ensure string type
        if(port is not None): self.config['port'] = int(port) # ensure integer type     
        if(password is not None): self.config['password'] = password
        pool = redis.ConnectionPool(host=self.config['host'], port=self.config['port'], password=self.config['password'],decode_responses=True)
        self.redis_instance = redis.Redis(connection_pool=pool)
        return

    def save(self, key, object):
        """
            Save "custome type" of value to the redis database
        """
        if(self.redis_instance is None): raise("Redis db connection not establised !")

        packed_object = pickle.dump(object, open("temp.p","w+"))
        self.redis_instance.set(str(key), packed_object)
        retrun 
    
    def load(self, key):
        """
            Restore the "custom type" of object with given key
        """
        if(self.redis_instance is None): raise("Redis db connection not establised !")

        packed_object = self.redis_instance.get(str(key))
        return pickle.load(packed_object)


