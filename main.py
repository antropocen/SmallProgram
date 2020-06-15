import argparse

from dispacher import Dispacher
from logic_handler import OptionsHandler
from models import User

parser = argparse.ArgumentParser(description='Program options')
parser.add_argument('--username', '-u', help='Login - user email', action='store')
parser.add_argument('--password', '-p', help='User password', action='store')
parser.add_argument('--new_password', '-n', help='New password', action='store')
parser.add_argument('--edit', '-e', help='Edit', action='store_true')
parser.add_argument('--delete', '-d', help='Delete user', action='store_true')
parser.add_argument('--list', '-l', help='List of user or massages', action='store_true')
parser.add_argument('--send', '-s', help='Send', action='store')
parser.add_argument('--to', '-t', help='Address of message', action='store')

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    dispacher = Dispacher()

    option_handler = OptionsHandler(
        args.username, args.password, args.new_password, args.edit, args.delete, args.list, args.send, args.to
    )

    if option_handler.create_user:
        result = dispacher.login_user(args.username, args.password)
        if result[1] == 1:
            dispacher.create_user(args.username, args.password)
            print('User {} created'.format(args.username))

    elif option_handler.list_all_users:
        if dispacher.all_users_list():
            print('All users list')

    elif option_handler.list_all_messages_for_user:
        result = dispacher.login_user(args.username, args.password)
        if isinstance(result[0], User):
            dispacher.list_messages_to_user(result[0])

    elif option_handler.change_password:
        result = dispacher.login_user(args.username, args.password)
        if isinstance(result[0], User):
            dispacher.change_password(result[0], args.new_password)
            print('Password Changed!')
        else:
            print('Password change failed!')

    elif option_handler.send_message:
        result = dispacher.login_user(args.username, args.password)
        if isinstance(result[0], User):
            if dispacher.send_message(args.to, result[0].email, args.send):
                print('Message send from user {} to user {}'.format(result[0].email, args.to))

    elif option_handler.delete_user:
        result = dispacher.login_user(args.username, args.password)
        if result[1] == 2:
            dispacher.delete_user(result[0])
            print("User {} deleted".format(result[0].email))

    else:
        print('Available options:')
        print('Create user: -u {user_name} -p {password}')
        print('Delete user: -u {user_name} -p {password} -d')
        print('List all users -l')
        print('Change password: -u {user_name} -p {password} -e -n {new_password}')
        print('Send message: -u {user_name} -p {password} to -t {receiver_name} -s {your message}')
        print('List all messages to specified user:  -u {user_name} -p {password} -l')
        dispacher.not_available_option()


