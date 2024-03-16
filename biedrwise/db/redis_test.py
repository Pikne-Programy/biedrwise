import redis


def init(r, *, clear=False):
    if clear:
        clear_all(r)
    r.set('row_id', 0)
    r.set('rec_id', 0)


def add_recipe(r):
    rec_id = r.get('rec_id')
    r.incr('rec_id')
    return rec_id


def add_row(r, rec_id, val_dict):
    row_id = r.get('row_id')
    r.incr('row_id')
    r.hset(f'row:{row_id}', mapping=val_dict)
    r.lpush(f'recipe:list:{rec_id}', row_id)
    return row_id


def del_recipe(r, rec_id):
    for row_id in r.lrange(f'recipe:list:{rec_id}', 0, -1):
        r.delete(f'row:{row_id}')
    r.delete(f'recipe:list:{rec_id}')


def clear_all(r):
    for key in r.scan_iter("*"):
        r.delete(key)


def print_recipe(r, rec_id):
    p = r.pipeline()
    for row_id in r.lrange(f'recipe:list:{rec_id}', 0, -1):
        p.hgetall(f'row:{row_id}')

    for h in p.execute():
        print(h)


if __name__ == '__init__':
    with redis.Redis(host='localhost', port=6379, decode_responses=True) as r:
        init(r, clear=True)

        rec_id = add_recipe(r)
        add_row(r, rec_id, {
            'name': 'jabłko',
            'count': 1.25,
            'price': 2.50
        })
        add_row(r, rec_id, {
            'name': 'banan',
            'count': 2.34,
            'price': 5.60
        })

        rec_id = add_recipe(r)
        add_row(r, rec_id, {
            'name': 'jabłko',
            'count': 1.25,
            'price': 2.50
        })
        add_row(r, rec_id, {
            'name': 'banan',
            'count': 2.34,
            'price': 5.60
        })

        print_recipe(r, 0)
        print_recipe(r, 1)

        del_recipe(r, 0)
