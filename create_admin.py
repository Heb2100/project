from models import User, engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin():
    db = SessionLocal()
    try:
        # 기존 admin 계정이 있는지 확인
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("Admin account already exists!")
            return

        # 새 admin 계정 생성
        hashed_password = pwd_context.hash("admin123!@#")
        admin = User(
            username="admin",
            email="admin@example.com",
            password=hashed_password,
            name="Administrator"
        )
        db.add(admin)
        db.commit()
        print("Admin account created successfully!")
        print("Username: admin")
        print("Password: admin123!@#")
    except Exception as e:
        print(f"Error creating admin account: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin() 