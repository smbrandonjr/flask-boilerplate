from flask_login import UserMixin
from app import login_manager
from app.models import FlaskModel, DatabaseConstant, CacheCompatibleEncryptedType


@login_manager.user_loader
def user_loader(user_id) -> "UserModel":
    user = UserModel.get_user_by_id(user_id)
    return user


class UserModel(FlaskModel, UserMixin):

    __tablename__ = 'users'

    id = DatabaseConstant.COLUMN(DatabaseConstant.PRIMARY_ID, primary_key=True)
    created_at = DatabaseConstant.COLUMN(
        DatabaseConstant.DATETIME,
        default=db.func.current_timestamp(),
        nullable=False
    )
    updated_at = DatabaseConstant.COLUMN(
        DatabaseConstant.DATETIME,
        default=db.func.current_timestamp(),
        nullable=True
    )
    last_login_at = DatabaseConstant.COLUMN(DatabaseConstant.DATETIME, nullable=True)
    email_address = DatabaseConstant.COLUMN(
        CacheCompatibleEncryptedType(
            DatabaseConstant.STRING(255),
            DatabaseConstant.ENCRYPTION_KEY,
            DatabaseConstant.AES_ENGINE,
            DatabaseConstant.PKCS5
        ), nullable=False)
    password = DatabaseConstant.COLUMN(
        CacheCompatibleEncryptedType(
            DatabaseConstant.STRING(255),
            DatabaseConstant.ENCRYPTION_KEY,
            DatabaseConstant.AES_ENGINE,
            DatabaseConstant.PKCS5
        ), nullable=True)

    @classmethod
    def get_user_by_id(cls, _id) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_user_by_email_address(cls, email_address) -> "UserModel":
        return cls.query.filter_by(email_address=email_address).first()
