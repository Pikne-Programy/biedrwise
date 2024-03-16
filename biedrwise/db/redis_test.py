from db import DataBase

if __name__ == '__main__':
    db = DataBase('redis', 6379)
    db.clear_all()

    rec_id = db.add_receipt({
        'jabłko': (1.25, 2.50),
        'banan': (2.34, 5.60)
    })

    rec_id = db.add_receipt({
        'jabłko': (1.25, 2.50),
        'banan': (2.34, 5.60)
    })

    db.print_receipt(0)
    db.print_receipt(1)

    # db.del_receipt(1)

    usr_id1 = db.add_user('user1')
    usr_id2 = db.add_user('user2')
    print(usr_id1, usr_id2)
    db.add_row_users(0, [usr_id1, usr_id2])
    db.add_row_users(1, [usr_id1])

    print(db.get_summary())
