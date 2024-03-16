import redis


class DataBase:
    def __init__(self, host='localhost', port=6379):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)
        # self.clear_all()
        if self.r.get('rec_id') is None:
            self.r.set('rec_id', 0)
        if self.r.get('row_id') is None:
            self.r.set('row_id', 0)
        if self.r.get('user_id') is None:
            self.r.set('user_id', 0)

    def __del__(self):
        self.r.close()

    def add_receipt(self, rows: dict[str, tuple[float, float]], data: tuple[str, float, int]):
        assert isinstance(rows, dict)
        rec_id = self.r.get('rec_id')
        self.r.incr('rec_id')
        for name, val in rows.items():
            assert len(val) == 2
            val_dict = {'name': name, 'price': val[0], 'count': val[1]}
            self._add_row(rec_id, val_dict)
        prices = [float(x[0]) for x in rows.values()]
        self.r.hset(f'receipt:{rec_id}:data', mapping={
            'date': data[0],
            'sum': sum(prices),
            'payed': data[2]
        })
        self.r.rpush("receipt:list", rec_id)
        return rec_id

    def _add_row(self, rec_id, val_dict):
        assert rec_id is not None
        row_id = self.r.get('row_id')
        self.r.incr('row_id')
        self.r.hset(f'row:{row_id}', mapping=val_dict)
        self.r.rpush(f'receipt:list:{rec_id}', row_id)
        return row_id

    def del_receipt(self, rec_id):
        assert rec_id is not None
        for row_id in self.r.lrange(f'receipt:list:{rec_id}', 0, -1):
            self.r.delete(f'row:{row_id}')
        self.r.delete(f'receipt:list:{rec_id}')

    def clear_all(self):
        for key in self.r.scan_iter("*"):
            self.r.delete(key)
        self.r.set('row_id', 0)
        self.r.set('rec_id', 0)
        self.r.set('user_id', 0)

    def print_receipt(self, rec_id):
        p = self.r.pipeline()
        for row_id in self.r.lrange(f'receipt:list:{rec_id}', 0, -1):
            p.hgetall(f'row:{row_id}')

        return [h for h in p.execute()]

    def get_receipt_data(self, rec_id):
        x = self.r.hgetall(f'receipt:{rec_id}:data')
        user_id = x['payed']
        x['name'] = self.r.hget(f'user:{user_id}', 'name')
        return x

    def get_receipts(self):
        res = []
        for rec_id in self.r.lrange(f'receipt:list', 0, -1):
            res += [self.r.hgetall(f'receipt:{rec_id}:data')]
        print(res)
        return res


    def add_user(self, name):
        user_id = self.r.get('user_id')
        self.r.incr('user_id')
        self.r.hset(f'user:{user_id}', mapping={
            'spending': 0,
            'name': name
        })
        self.r.rpush('user:list', user_id)
        return user_id

    def add_row_users(self, row_id, users):
        assert row_id is not None
        assert users is not None
        self.r.delete(f'row:{row_id}:users')
        self.r.rpush(f'row:{row_id}:users', *users)
        for user_id in users:
            price = self.r.hget(f'row:{row_id}', 'price')
            frac_price = float(price) / len(users)
            self.r.hincrbyfloat(f'user:{user_id}', 'spending', frac_price)

    def get_user_spending(self, user_id):
        assert user_id is not None
        return self.r.hget(f'user:{user_id}', 'spending')

    def get_summary(self):
        summary = []
        for user_id in self.r.lrange(f'user:list', 0, -1):
            user_data = self.r.hgetall(f'user:{user_id}')
            summary += [(user_data['name'], float(user_data['spending']))]
        return summary
