import redis


class DataBase:
    def __init__(self, host='localhost', port=6379):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)
        if self.r.get('rec_id') is None:
            self.r.set('rec_id', 0)
        if self.r.get('row_id') is None:
            self.r.set('row_id', 0)
        if self.r.get('user_id') is None:
            self.r.set('user_id', 0)

    def __del__(self):
        self.r.close()

    def add_recipe(self):
        rec_id = self.r.get('rec_id')
        self.r.incr('rec_id')
        return rec_id

    def add_row(self, rec_id, val_dict):
        assert rec_id is not None
        row_id = self.r.get('row_id')
        self.r.incr('row_id')
        self.r.hset(f'row:{row_id}', mapping=val_dict)
        self.r.rpush(f'recipe:list:{rec_id}', row_id)
        return row_id

    def del_recipe(self, rec_id):
        assert rec_id is not None
        for row_id in self.r.lrange(f'recipe:list:{rec_id}', 0, -1):
            self.r.delete(f'row:{row_id}')
        self.r.delete(f'recipe:list:{rec_id}')

    def clear_all(self):
        for key in self.r.scan_iter("*"):
            self.r.delete(key)
        self.r.set('row_id', 0)
        self.r.set('rec_id', 0)
        self.r.set('user_id', 0)

    def print_recipe(self, rec_id):
        p = self.r.pipeline()
        for row_id in self.r.lrange(f'recipe:list:{rec_id}', 0, -1):
            p.hgetall(f'row:{row_id}')

        for h in p.execute():
            print(h)

    def add_user(self):
        user_id = self.r.get('user_id')
        self.r.incr('user_id')
        self.r.set(f'user:{user_id}:spending', 0)
        return user_id

    def add_row_users(self, row_id, users):
        assert row_id is not None
        assert users is not None
        self.r.delete(f'row:{row_id}:users')
        self.r.rpush(f'row:{row_id}:users', *users)
        for user_id in users:
            price = self.r.hget(f'row:{row_id}', 'price')
            frac_price = float(price) / len(users)
            self.r.incrbyfloat(f'user:{user_id}:spending', frac_price)
