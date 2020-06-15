import re
from typing import Union, List

from clcrypto import generate_salt
from models import User, Message, create_connection, get_cursor


class WrongParameterError(Exception):
    """Error when wrong params set is given"""
    pass


def email_validator(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if (re.search(regex, email)):
        return True
    else:
        raise Exception('Username {} is not valid e-mail address. Please enter email.'.format(email))
        return False


def try_connect_db():
    try:
        connection = create_connection(db_name="war2")
        return connection
    except Exception as err:
        print("Database connection failed: {}".format(err))
        return False,


def password_validator(password):
    if len(password) < 8:
        raise Exception('The minimum password length is 8! ')


class Dispacher:
    """HINT: USERNAME == EMAIL """

    def login_user(self, username: str, password: str) -> Union[User, None]:
        """:
        Args:
            username (str): user email as an username
            password (str): user password

        Returns:
            tab[User, int]
            res[None, -1]  if not valid email
            res[None, -2]  if not valid password / login failed
            res[None,  1]  if given username (email) not in database
            res[User,  2]  object class User when login succeeded
        """
        res = [None, 0]
        if not email_validator(username):
            res[1] = -1
            return res
        connection = try_connect_db()
        cursor = get_cursor(connection)
        user = User()
        user.email = username
        db_user = user.load_by_email(cursor, username)
        if db_user is None:
            print('User {} does not exist in database'.format(username))
            cursor.close()
            connection.close()
            res[1] = 1
            return res
        else:
            print('Username {} exists in database'.format(username))
            valid = db_user.check_password(password)
            cursor.close()
            connection.close()
        if valid:
            print("Login succeeded")
            res[0] = db_user
            res[1] = 2
            return res
        else:
            print("Password is incorrect. Login failed")
            res[1] = -2
            return res

    def create_user(self, new_username: str, password: str) -> User:
        if not email_validator(new_username):
            return False
        password_validator(password)
        connection = try_connect_db()
        cursor = get_cursor(connection)
        salt = generate_salt()
        user = User()
        user.email = new_username
        user.set_password(password, salt)
        try:
            user.save(cursor)
            cursor.close()
            connection.close()
            return True
        except Exception as err:
            print('Data not saved to database due to the error:  {}'.format(err))
            cursor.close()
            connection.close()
            return False

    def all_users_list(self) -> List[Union[User, None]]:
        """Print all users which are in database"""
        connection = try_connect_db()
        cursor = get_cursor(connection)
        user = User()
        all_users = user.load_all(cursor)
        cursor.close()
        connection.close()
        if all_users:
            print("All users:")
            for user in all_users:
                print(user.email)
        else:
            print("There are no any users in database")

    def list_messages_to_user(self, user: User) -> List[Union[Message, None]]:
        """Return list of all messages in database for specific user"""
        connection = try_connect_db()
        cursor = get_cursor(connection)
        message = Message()
        all_messages = message.load_all(cursor)

        print("All messages to user {}:".format(user.email))
        count = 0
        for item in all_messages:
            if item.to_id == user.id:
                count += 1
                print("Message from {} sent on {}: {}".format(user.load_by_id(cursor, item.from_id).email,
                                                              item.creation_date, item.text))
        if count == 0:
            print("Inbox empty!")
        cursor.close()
        connection.close()

    def change_password(self, user: User, new_password: str) -> None:
        password_validator(new_password)
        if user.check_password(new_password):
            raise Exception("given password is the same as the previous one")
        connection = try_connect_db()
        cursor = get_cursor(connection)
        salt = generate_salt()
        user.set_password(new_password, salt)
        user.save(cursor)
        cursor.close()
        connection.close()
        return True

    def send_message(self, adress: User, sender: User, message_text: str) -> Message:
        """Create message to adress (User) to sender (User) into database."""

        connection = try_connect_db()
        cursor = get_cursor(connection)
        from_user = User()
        to_user = User()
        from_user = from_user.load_by_email(cursor, sender)
        to_user = to_user.load_by_email(cursor, adress)
        if not to_user:
            print("User {} does not exist. Message cannot be sent.".format(adress))
            cursor.close()
            connection.close()
            return False
        message = Message()
        message.from_id = from_user.id
        message.to_id = to_user.id
        message.text = message_text
        try:
            message.save(cursor)
        except Exception as err:
            print('Data not saved to database due to the error:  {}'.format(err))
            cursor.close()
            connection.close()
            return False
        cursor.close()
        connection.close()
        return True

    def delete_user(self, user: User) -> None:
        connection = try_connect_db()
        cursor = get_cursor(connection)
        result = user.delete(cursor)
        cursor.close()
        connection.close()
        return result

    def not_available_option(self):
        raise WrongParameterError("Wrong parameters set up!")
