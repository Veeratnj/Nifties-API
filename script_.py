"""
Script to create a superadmin user if not exists
"""

from app.db.db import SessionLocal
from app.models.models import User, UserRole
from app.utils.security import SecurityUtils
import sys

def create_superadmin(email, username, password, name="Super Admin", phone=None):
	db = SessionLocal()
	try:
		existing = db.query(User).filter(User.role == UserRole.SUPERADMIN).first()
		if existing:
			print(f"Superadmin already exists: {existing.email}")
			return

		password_hash = SecurityUtils.hash_password(password)
		superadmin = User(
			email=email,
			username=username,
			name=name,
			password_hash=password_hash,
			phone=phone,
			role=UserRole.SUPERADMIN,
			is_active=True,
			is_verified=True,
			kyc_verified=True
		)
		db.add(superadmin)
		db.commit()
		db.refresh(superadmin)
		print(f"Superadmin created: {superadmin.email}")
	except Exception as e:
		db.rollback()
		print(f"Error creating superadmin: {e}")
	finally:
		db.close()

if __name__ == "__main__":
	# You can pass email, username, password as arguments, or use defaults for demo
	if len(sys.argv) >= 4:
		email = sys.argv[1]
		username = sys.argv[2]
		password = sys.argv[3]
		name = sys.argv[4] if len(sys.argv) > 4 else "Super Admin"
		phone = sys.argv[5] if len(sys.argv) > 5 else None
	else:
		email = "superadmin@example.com"
		username = "superadmin"
		password = "SuperSecret123"
		name = "Super Admin"
		phone = None
	create_superadmin(email, username, password, name, phone)
