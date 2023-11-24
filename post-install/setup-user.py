import string
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from argon2 import PasswordHasher
from secrets import choice
from uuid import uuid4, UUID
import sqlite3


@dataclass
class Options:
    db_path: Path
    username: str
    # ask_password: str # don't feel like implementing this right now.
    is_admin: bool


@dataclass
class User:
    id: UUID
    username: str
    password: str
    hash: str
    is_admin: bool


def collect_options() -> Options:
    parser = ArgumentParser(description='Create a new user in a horreum.db database for a horreum instance.')
    parser.add_argument('username', type=str, help='Username for the new user.')
    parser.add_argument('path', type=str, help='Path to the horreum database file.')
    # parser.add_argument('--ask-password', action='store_true')
    parser.add_argument('--create-admin', action='store_true')
    args = parser.parse_args()

    return Options(
        db_path=Path(args.path).expanduser().resolve(),
        username=args.username,
        # ask_password=args.ask_password,
        is_admin=args.create_admin,
    )


def generate_password() -> str:
    return ''.join(choice(string.ascii_letters + string.digits) for i in range(16))


def store_values(db_path: Path, user: User) -> bool:
    try:
        con = sqlite3.connect(
            database=db_path,
        )
        cur = con.cursor()
        command = f"INSERT INTO user(id, name, password, admin) VALUES('{user.id}', '{user.username}', '{user.hash}', '{user.is_admin}')"
        cur.execute(command)
        con.commit()
    except Exception as e:
        print(e)
        return False

    return True


def print_message(options: Options, user: User):
    print(f'New user created in {options.db_path}')
    print('\nWRITE DOWN THIS INFO!\n')
    print(f'\tUsername: {user.username}')
    print(f'\tPassword: {user.password}')


def main():
    options = collect_options()

    password = generate_password()
    ph = PasswordHasher()

    user = User(
        id=uuid4(),
        username=options.username,
        password=password,
        hash=ph.hash(password),
        is_admin=options.is_admin,
    )

    if not store_values(options.db_path, user):
        print("Failure.")
        return 1

    print_message(options, user)

    return 0


if __name__ == '__main__':
    main()
