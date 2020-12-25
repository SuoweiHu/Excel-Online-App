import redis

pool = redis.ConnectionPool(host='10.0.0.96', port=9736, password='ZGzjshzsjgqjfdl9@',decode_responses=True)
r = redis.Redis(connection_pool=pool)
r.set('food', 'mutton', ex=3)       # key是"food" value是"mutton" 将键值对存入redis缓存
print(r.get('food'))                # mutton 取出键food对应的值