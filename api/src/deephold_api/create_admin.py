"""CLI to create an admin user.

Usage:
    python -m deephold_api.create_admin <email> <password> [--name NAME]

Example:
    python -m deephold_api.create_admin admin@example.com secret123 --name "Admin"
"""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import select

from deephold_api.auth import hash_password
from deephold_api.db_session import get_sessionmaker
from deephold_api.models import User, init_app_schema


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("email", help="User email")
    parser.add_argument("password", help="User password")
    parser.add_argument("--name", default=None, help="Display name")
    args = parser.parse_args(argv)

    # Ensure schema exists
    init_app_schema()

    session = get_sessionmaker()()
    try:
        existing = session.execute(
            select(User).where(User.email == args.email)
        ).scalar_one_or_none()
        if existing:
            print(f"User {args.email} already exists (id={existing.user_id}). Updating password.")
            existing.password_hash = hash_password(args.password)
            existing.is_admin = True
            if args.name:
                existing.name = args.name
            session.commit()
            print(f"Updated admin user: {args.email}")
            return 0

        user = User(
            email=args.email,
            password_hash=hash_password(args.password),
            name=args.name,
            is_admin=True,
            is_active=True,
        )
        session.add(user)
        session.commit()
        print(f"Created admin user: {args.email} (id={user.user_id})")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
