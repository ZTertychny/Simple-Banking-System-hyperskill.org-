# Write your code here
import random
import sqlite3


class BankingSystem:
    """Class which describes functionality of Banking system. It creates new accounts, check cards number of cards for Luhn algorithm,
    creates database with informational about client's cards and balances."""

    def create_account(self):
        """Make a new card and return a tuple with number of new card and pin for it"""
        card_num = 400000
        pin = ''
        counter = 0
        while counter < 9:
            temp_num = random.randint(0, 9)
            card_num = card_num * 10 + temp_num
            if counter < 4:
                pin += str(random.randint(0, 9))
            counter += 1
        card_num = self.Luhn_algo(card_num)
        cards_tuple = (card_num, pin)
        print(f'Your card has been created\nYour card number:\n{card_num}\nYour card PIN:\n{pin}')
        return cards_tuple

    def Luhn_algo(self, card_num):
        """Receive a number of created card and return 16 digit card where the las symbol is defined by Luhn algorithm"""
        card_num_list = [int(i) for i in str(card_num)]
        sum_of_num = 0
        last_num = 0
        for ind in range(len(card_num_list)):
            if ind % 2 == 0:
                card_num_list[ind] = int(card_num_list[ind]) * 2
        for ind in range(len(card_num_list)):
            if card_num_list[ind] > 9:
                card_num_list[ind] = card_num_list[ind] - 9
        for el in card_num_list:
            sum_of_num += el
        if sum_of_num % 10 == 0:
            last_num = 0
        else:
            for x in range(1, 10):
                if (sum_of_num + x) % 10 == 0:
                    last_num = x
                    break
        card_num = card_num * 10 + last_num
        return str(card_num)

    def create_connection(self):
        """Make a connection woth Database"""
        conn = Database()
        conn.create_connection('card.s3db')
        conn.create_table('''CREATE TABLE IF NOT EXISTS card(
                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            number TEXT,
                            pin TEXT,
                            balance INTEGER DEFAULT 0);
                        ''')
        return conn

    def main(self):
        """Main function of this code which starts the program"""
        conn = self.create_connection()
        bool_check = True
        while bool_check:
            act = int(input('1. Create an account\n2. Log into account\n0. Exit\n'))
            if act == 1:
                temp_card = [self.create_account()]
                while conn.retrieve_data(f"SELECT * FROM card WHERE number = '{temp_card[0][0]}'", "1") is not None:
                    temp_card = self.create_account()
                conn.insert_data('INSERT INTO card(number, pin) VALUES(?, ?)', temp_card)

            elif act == 2:
                check_card = input('Enter your card number:\n')
                check_pin = input('Enter your PIN:\n')
                if conn.retrieve_data(f"SELECT * FROM card WHERE number = '{check_card}' and pin = '{check_pin}'",
                                      "1") is not None:
                    print('You have successfully logged in!')
                    while True:
                        act_in_ac = int(
                            input('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0.Exit\n'))

                        if act_in_ac == 1:
                            res = conn.retrieve_data(
                                f"SELECT balance FROM card WHERE number = '{check_card}' and pin = '{check_pin}'", "1")
                            print(res[0])

                        elif act_in_ac == 2:
                            income = int(input('Enter income:\n'))
                            cur_balance = conn.retrieve_data(
                                f"SELECT balance FROM card WHERE number = '{check_card}' and pin = '{check_pin}'",
                                "1")
                            income = (str(income + int(cur_balance[0])),)
                            conn.update_data(f"UPDATE card SET balance = ? WHERE number = '{check_card}'", income)
                            print('Income was added!')

                        elif act_in_ac == 3:
                            print('Transfer')
                            target_num_card = (input('Enter card number:\n'),)
                            check_for_luhn = self.Luhn_algo(int(target_num_card[0][:-1]))
                            if target_num_card[0] != check_for_luhn:
                                print('Probably you made a mistake in the card number. Please try again!')

                            elif conn.retrieve_data(f"SELECT * FROM card WHERE number = '{target_num_card[0]}'",
                                                    "1") is None:
                                print('Such a card does not exist.')

                            elif target_num_card[0] == check_card[0]:
                                print("You can't transfer money to the same account!")

                            else:
                                cur_balance = conn.retrieve_data(
                                    f"SELECT balance FROM card WHERE number = '{check_card}'", "1")
                                money_trans = (input('Enter how much money you want to transfer:\n'),)
                                if int(money_trans[0]) > int(cur_balance[0]):
                                    print('Not enough money!')
                                else:
                                    new_balance = (int(cur_balance[0]) - int(money_trans[0]),)
                                    conn.update_data(
                                        f"UPDATE card SET balance = ? WHERE number = '{target_num_card[0]}'",
                                        money_trans)
                                    conn.update_data(f"UPDATE card SET balance = ? WHERE number = '{check_card}'",
                                                     new_balance)
                        elif act_in_ac == 4:
                            conn.delete_data(f"DELETE FROM card WHERE number = '{check_card}'")
                            print('The account has been closed!')
                            break
                        elif act_in_ac == 5:
                            break
                        else:
                            bool_check = False
                            break
                else:
                    print('Wrong card number or PIN!')
            else:
                bool_check = False


class MyEr(Exception):
    """Class for raising user's exceptions"""


def __init__(self, msg):
    self.msg = msg


class Database:
    """Create Database"""

    def __init__(self):
        self.conn = None
        self.cur = None

    def create_connection(self, db_name):
        """Receive db_name as name of new database. If there isn't such file with db the creates a new one"""
        self.conn = sqlite3.connect(f'{db_name}')
        self.cur = self.conn.cursor()
        return self.cur

    def create_table(self, table):
        """Receive table line SQL query: Create TABLE name(......);"""
        if self.cur and self.conn:
            self.cur.execute(f'{table}')
            return self.conn.commit()
        else:
            raise MyEr('There is no connection!')

    def insert_data(self, insert_data, data):
        """Receive insert_data in form of SQL query: INSERT INTO name_table VALUES()
        data is the var which receives new values, data should be the list with the tuple inside"""
        if self.cur and self.conn:
            self.cur.executemany(insert_data, data)
            return self.conn.commit()
        else:
            raise MyEr('There is no connection!')

    def update_data(self, update_query, data):
        """Receive query in the form of SQL query to update existing table"""
        if self.cur and self.conn:
            self.cur.execute(update_query, data)
            return self.conn.commit()
        else:
            raise MyEr('There is no connection!')

    def retrieve_data(self, query, qty_of_res):
        """Receive qty_of_res as quantity of lines. Can be from 1 to all.
        Receive query as SQL query (SELECT ... FROM ...)"""
        if self.cur and self.conn:
            self.cur.execute(f'{query}')
            if qty_of_res == '1':
                return self.cur.fetchone()
            elif qty_of_res == 'all':
                return self.cur.fetchall()
            else:
                return self.cur.fetchmany(int(qty_of_res))
        else:
            raise MyEr('There is no connection!')

    def delete_data(self, query):
        """Receive SQL query in var query which deletes data"""
        if self.cur and self.conn:
            self.cur.execute(f'{query}')
            return self.conn.commit()
        else:
            raise MyEr('There is no connection!')


start = BankingSystem()
start.main()
