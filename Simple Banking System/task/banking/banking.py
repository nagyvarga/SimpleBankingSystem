import random
import sqlite3


database_connection = sqlite3.connect('card.s3db')
database_cursor = database_connection.cursor()
database_cursor.execute("CREATE TABLE if not exists card (id INTEGER, number TEXT, pin TEXT,"
                        "balance INTEGER DEFAULT 0);")
database_connection.commit()


MAIN_MENU = "\n1. Create an account\n2. Log into account\n0. Exit"
LOGGED_IN_MENU = "\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit"
exit_status = False


class Bank:
    """Create or log into account in banking system."""
    # accounts = {}
    BIN = "400000"  # Bank Identification Number

    def create_account(self):
        """Create an account by a card number and its pin and set balance to 0."""
        account_identifier = "".join([str(num) for num in random.sample(range(10), 9)])
        first_fifteen_digit = self.BIN + account_identifier
        checksum = self.create_checksum(first_fifteen_digit)
        card_number = first_fifteen_digit + str(checksum)
        pin = "".join([str(num) for num in random.sample(range(10), 4)])
        balance = 0
        print("\nYour card has been created")
        print(f"Your card number:\n{card_number}\nYour card PIN:\n{pin}")
        # self.accounts[card_number] = [pin, balance]
        # fetching max id from database
        database_cursor.execute("SELECT id FROM card;")
        ids = [x[0] for x in database_cursor.fetchall()]
        if ids:
            max_id = max(ids) + 1
        else:
            max_id = 1
        # insert new account into database
        database_cursor.execute(f"INSERT INTO card VALUES ({max_id}, {card_number}, {pin}, {balance});")
        database_connection.commit()

    def create_checksum(self, fifteen_digit):
        """Create checksum digit of the card using Luhn algorithm.

        1. Multiply odd digits by 2  / the step of the card number starts from 1 /
        2. Subtract 9 from numbers over 9
        3. Add all numbers
        4. Return (10 - sum_up % 10) % 10
        """
        duplicate_odd_digits = [int(fifteen_digit[i - 1]) * 2 if i % 2 else
                                int(fifteen_digit[i - 1]) for i in range(1, 16)]
        subtract_nine = [digit - 9 if digit > 9 else digit for digit in duplicate_odd_digits]
        sum_up = sum(subtract_nine)
        return (10 - sum_up % 10) % 10

    def check_card_number(self, card_number):
        """Check card number in all accounts."""
        database_cursor.execute(f"SELECT number FROM card WHERE number = {card_number};")
        result = database_cursor.fetchall()
        return result[0][0] == card_number if result else False
        # return card_number in self.accounts.keys()

    def check_pin(self, card_number, pin):
        """Check PIN of the card number."""
        database_cursor.execute(f"SELECT pin FROM card WHERE number = {card_number};")
        result = database_cursor.fetchall()
        print(result)
        return result[0][0] == pin
        # return self.accounts[card_number][0] == pin

    def log_into_account(self, card_number, pin):
        """..."""
        if self.check_card_number(card_number):
            if self.check_pin(card_number, pin):
                return card_number
            else:
                return None
        else:
            return None

    def balance(self, card_number):
        """Return the balance of the actual account."""
        database_cursor.execute(f"SELECT balance FROM card WHERE number = {card_number};")
        return database_cursor.fetchone()[0]
        # return self.accounts[card_number][1]

    def add_income(self, card_number, income):
        """Deposit money to the account"""
        old_balance = self.balance(card_number)
        database_cursor.execute(f"UPDATE card SET balance = {old_balance + income} WHERE number = {card_number};")
        database_connection.commit()

    def do_transfer(self, card_number, transfer_number, money):
        self.add_income(card_number, -money)
        self.add_income(transfer_number, money)

    def close_account(self, card_number):
        """Close and delete from database the account"""
        database_cursor.execute(f"DELETE FROM card WHERE number = {card_number};")
        database_connection.commit()


def wrong_account():
    print("\nWrong card number or PIN!")


def logged_in_menu(actual_card_number):
    global exit_status
    print("\nYou have successfully logged in!")
    while True:
        print(LOGGED_IN_MENU)
        logged_user_input = input()
        if logged_user_input == "0":
            exit_status = True
            break
        elif logged_user_input == "1":
            print(f"\nBalance: {my_bank.balance(actual_card_number)}")
        elif logged_user_input == "2":
            print("\nEnter income:")
            income = int(input())
            my_bank.add_income(actual_card_number, income)
            print("Income was added!")
        elif logged_user_input == "3":
            print("\nEnter card number:")
            transfer_card_number = input()
            if len(transfer_card_number) == 16:
                transfer_card_checksum = my_bank.create_checksum(transfer_card_number[:-1])
                if str(transfer_card_checksum) == transfer_card_number[-1]:
                    if transfer_card_number == actual_card_number:
                        print("You can't transfer money to the same account!")
                    else:
                        if my_bank.check_card_number(transfer_card_number):
                            print("Enter how much money you want to transfer:")
                            transfer_money = int(input())
                            if my_bank.balance(actual_card_number) >= transfer_money:
                                my_bank.do_transfer(actual_card_number, transfer_card_number, transfer_money)
                                print("Success!")
                            else:
                                print("Not enough money!")
                        else:
                            print("Such a card does not exist.")
                else:
                    print("Probably you made a mistake in the card number. Please try again!")
        elif logged_user_input == "4":
            my_bank.close_account(actual_card_number)
            print("\nThe account has been closed!")
            break
        elif logged_user_input == "5":
            print("\nYou have successfully logged out!")
            break


# Banking program starts here
my_bank = Bank()

while True:
    if exit_status:
        break

    print(MAIN_MENU)
    user_input = input()
    if user_input == "0":
        break
    elif user_input == "1":
        my_bank.create_account()
    elif user_input == "2":
        print("\nEnter your card number:")
        user_card_number = input()
        print("Enter your PIN:")

        user_pin = input()
        checked_card_number = my_bank.log_into_account(user_card_number, user_pin)

        if checked_card_number is None:
            wrong_account()
        else:
            logged_in_menu(checked_card_number)

print("\nBye!")
