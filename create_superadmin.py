from getpass import getpass

from sqlalchemy import select

from model.database import SessionLocal
from model.user import User
from service.user_service import UserService


def main():
    db = SessionLocal()

    try:
        existing_superadmin = db.scalar(
            select(User).where(User.role == "superadmin")
        )

        if existing_superadmin:
            print("A superadmin already exists.")
            return

        name = input("Enter superadmin name: ").strip()
        email = input("Enter superadmin email: ").strip().lower()
        phone = input("Enter superadmin phone: ").strip()

        password = getpass("Enter superadmin password: ")
        confirm_password = getpass("Confirm password: ")

        if not name or not email or not phone:
            print("Name, email, and phone are required.")
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        if len(password) < 8:
            print("Password must be at least 8 characters.")
            return

        service = UserService(db)

        if service.repository.get_by_email(email):
            print("This email is already registered.")
            return

        if service.repository.get_by_phone(phone):
            print("This phone number is already registered.")
            return

        # Use the same password-hashing method as normal registration.
        hashed_password = service.hash_password(password)

        superadmin = User(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password,
            role="superadmin"
        )

        service.repository.create(superadmin)

        print("Superadmin created successfully.")
        print(f"Email: {email}")

    except Exception as error:
        db.rollback()
        print(f"Error creating superadmin: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    main()