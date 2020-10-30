import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0
            )''')
conn.commit()


def print_menu():
    print('\n1. Create an account', '2. Log into account', '0. Exit', sep='\n')


def generate_card():
    iin = 400000
    card_number_ten_digits = random.randint(1000000000, 9999999999)
    card_number = str(iin) + str(card_number_ten_digits)
    card_number = card_number[:-1]
    random_card_without_last_digit = [int(n) for n in card_number]
    card_number = [int(n) * 2 if i % 2 == 0 else int(n) for i, n in enumerate(card_number)]
    card_number = [n - 9 if n > 9 else n for n in card_number]
    check_digit = sum(card_number) * 9 % 10
    random_card_without_last_digit.append(check_digit)
    converted_card_to_string = [str(n) for n in random_card_without_last_digit]

    final_card_with_check_digit = ''
    for n in converted_card_to_string:
        final_card_with_check_digit += n

    return final_card_with_check_digit


def card_number_check(card_transfer):
    card_number = card_transfer
    card_number_check_digit = card_number[-1:]
    card_number_without_check_digit = card_number[:-1]
    card_number = [int(n) for n in card_number_without_check_digit]
    # Luhn Begin
    double_odd = [n * 2 if i % 2 == 0 else n for i, n in enumerate(card_number)]
    numbers = [n - 9 if n > 9 else n for n in double_odd]
    sum_digits = sum(numbers)
    multiply_by_nine = sum_digits * 9
    mod_of_multiply_by_nine = multiply_by_nine % 10
    return mod_of_multiply_by_nine == int(card_number_check_digit)


def create_account():
    card_number = generate_card()
    card_pin = random.randint(1000, 9999)
    cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (str(card_number), str(card_pin)))
    conn.commit()
    return card_number, card_pin


def card_balance(card_number):
    cur.execute('SELECT * FROM card WHERE number = ?', (card_number, ))
    row = cur.fetchone()
    return row[3]


def add_income(card_number):
    cur.execute('SELECT * FROM card WHERE number = ?', (card_number, ))
    row = cur.fetchone()
    balance = row[3]
    print("\nEnter income:")
    income = int(input())
    cur.execute('UPDATE card SET balance = ? WHERE number = ?', (balance + income, card_number))
    conn.commit()
    print('Income was added!\n')


def do_transfer(card_number):
    print('\nTransfer')
    print('Enter card number:')
    card_transfer = input()
    if card_number_check(card_transfer):
        cur.execute('SELECT * FROM card WHERE number = ?', (card_transfer, ))
        row = cur.fetchall()
        if len(row) > 0:
            if card_transfer == card_number:
                print("You can't transfer money to the same account!\n")
            else:
                balance_do_transfer = row[0][3]
                print('Enter how much money you want to transfer:')
                transfer_value = int(input())
                balance = card_balance(card_number)
                if transfer_value > balance:
                    print('Not enough money!\n')
                else:
                    cur.execute('UPDATE card SET balance = ? WHERE number = ?', (balance - transfer_value, card_number))
                    conn.commit()
                    cur.execute('UPDATE card SET balance = ? WHERE number = ?', (balance_do_transfer + transfer_value,
                                                                                 card_transfer))
                    conn.commit()
                    print('Success!\n')
        else:
            print('Such a card does not exist.\n')
    else:
        print('Probably you made a mistake in the card number. Please try again!\n')


def close_account(id):
    cur.execute('DELETE FROM card WHERE id=?', (id, ))
    conn.commit()
    print('\nThe account has been closed!')


def account_balance(id, card_number):
    while True:
        print('1. Balance')
        print('2. Add income')
        print('3. Do transfer')
        print('4. Close account')
        print('5. Log out')
        print('0. Exit')
        balance_choice = int(input())

        if balance_choice == 1:
            card_balance(card_number)
        elif balance_choice == 2:
            add_income(card_number)
        elif balance_choice == 3:
            print(f'\nBalance: {do_transfer(card_number)}\n')
        elif balance_choice == 4:
            close_account(id)
            break
        elif balance_choice == 5:
            print('\nYou have successfully logged out!')
            break
        elif balance_choice == 0:
            print('Bye!\n')
            exit()


def log_account():
    print('Enter your card number:')
    card_number_log = input()
    print('Enter your PIN:')
    pin_number_log = input()
    cur.execute('SELECT * FROM card WHERE number=? AND pin=?', (card_number_log, pin_number_log))
    row = cur.fetchall()

    if len(row) > 0:
        print('\nYou have successfully logged in!\n')
        account_balance(row[0][0], row[0][1])
    else:
        print('\nWrong card number or PIN!')


while True:
    print_menu()
    menu_choice = str(input())
    if menu_choice == '1':
        card, pin = create_account()
        print('\nYour card has been created', 'Your card number:', f'{card}', sep='\n')
        print('Your card PIN:', f'{pin}', sep='\n')
    elif menu_choice == '2':
        log_account()
    elif menu_choice == '0':
        print('\nBye!')
        break