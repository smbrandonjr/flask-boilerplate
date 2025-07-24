import logging
import json
import pytz
from datetime import datetime
from decimal import Decimal
from flask import abort, current_app
from sqlalchemy import ForeignKey as sa_foreign_key
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship as sa_relationship, Mapped as sa_mapped
from sqlalchemy.orm.state import InstanceState
import sqlalchemy.schema as sa_schema
import sqlalchemy.types as sa_type
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from app import db, log_exception
from app.config import Config

logger = logging.getLogger(__name__)

class FlaskModel(db.Model):

    __abstract__ = True

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]

            setattr(self, property, value)

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log_exception(current_app.logger, "models.FlaskModel.save() - SQLAlchemyError", e, level='error')
            db.session.rollback()
            db.session.close()
            # Handle original error if available, otherwise use the main error
            error_msg = str(getattr(e, 'orig', e))
            abort(422, description=error_msg)
        except Exception as e:
            log_exception(current_app.logger, "models.FlaskModel.save() - Generic Exception", e, level='error')
            db.session.rollback()
            db.session.close()
            abort(422, description=str(e))

    def delete(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log_exception(current_app.logger, "models.FlaskModel.delete() - SQLAlchemyError", e, level='error')
            db.session.rollback()
            db.session.close()
            # Handle original error if available, otherwise use the main error
            error_msg = str(getattr(e, 'orig', e))
            abort(422, description=error_msg)
        except Exception as e:
            log_exception(current_app.logger, "models.FlaskModel.delete() - Generic Exception", e, level='error')
            db.session.rollback()
            db.session.close()
            abort(422, description=str(e))
        return

    @classmethod
    def rollback(cls) -> None:
        try:
            db.session.rollback()
        except SQLAlchemyError as e:
            log_exception(current_app.logger, "models.FlaskModel.rollback() - SQLAlchemyError", e, level='error')
            abort(500, description="Database rollback failed")
        except Exception as e:
            log_exception(current_app.logger, "models.FlaskModel.rollback() - Generic Exception", e, level='error')
            abort(500, description="Unexpected error during rollback")
        finally:
            db.session.close()

    def json(self):
        readd_instance_state = False
        readd_instance_state_value = None
        for member in list(self.__dict__):
            if isinstance(self.__dict__[member], datetime):
                self.__dict__[member] = str(self.__dict__[member])
            elif isinstance(self.__dict__[member], InstanceState):
                readd_instance_state = True
                readd_instance_state_value = self.__dict__[member]
                del self.__dict__[member]
            elif isinstance(self.__dict__[member], Decimal):
                self.__dict__[member] = float(self.__dict__[member])
        result = json.loads(json.dumps(self.__dict__))
        if readd_instance_state:
            self.__dict__['_sa_instance_state'] = readd_instance_state_value
        return result

    def dumped_json(self):
        readd_instance_state = False
        readd_instance_state_value = None
        for member in list(self.__dict__):
            if isinstance(self.__dict__[member], datetime):
                self.__dict__[member] = str(self.__dict__[member])
            elif isinstance(self.__dict__[member], InstanceState):
                readd_instance_state = True
                readd_instance_state_value = self.__dict__[member]
                del self.__dict__[member]
            elif isinstance(self.__dict__[member], Decimal):
                self.__dict__[member] = float(self.__dict__[member])
        result = json.loads(json.dumps(self.__dict__))
        if readd_instance_state:
            self.__dict__['_sa_instance_state'] = readd_instance_state_value
        return json.dumps(result)


class CacheCompatibleEncryptedType(EncryptedType):
    cache_ok = True


class DatabaseConstant:

    @staticmethod
    def current_timestamp():
        return datetime.now(pytz.UTC)

    PKCS5 = 'pkcs5'
    ENCRYPTION_KEY = Config.ENCRYPTION_KEY

    ENCRYPTED_TYPE = EncryptedType
    AES_ENGINE = AesEngine

    COLUMN = sa_schema.Column
    RELATIONSHIP = sa_relationship
    MAPPED = sa_mapped
    FOREIGN_KEY = sa_foreign_key
    ENUM = sa_type.Enum

    PRIMARY_ID = sa_type.BIGINT
    DATE = sa_type.Date
    DATETIME = sa_type.DateTime
    BOOLEAN = sa_type.BOOLEAN
    INTEGER = sa_type.INTEGER
    FLOAT = sa_type.FLOAT
    JSON = sa_type.JSON
    TEXT = sa_type.TEXT

    @staticmethod
    def DECIMAL(precision=65, scale=2):
        return sa_type.DECIMAL(precision, scale)

    @staticmethod
    def STRING(length):
        return sa_type.String(length)


class AdminSettings(db.Model, FlaskModel):

    __tablename__ = 'admin_settings'

    id = DatabaseConstant.COLUMN(DatabaseConstant.PRIMARY_ID, primary_key=True)
    datatype = DatabaseConstant.COLUMN(DatabaseConstant.STRING(100), nullable=False)
    key = DatabaseConstant.COLUMN(DatabaseConstant.STRING(100), nullable=False, unique=True)
    value = DatabaseConstant.COLUMN(DatabaseConstant.STRING(255), nullable=False)
    description = DatabaseConstant.COLUMN(DatabaseConstant.STRING(255), nullable=True)
    created_at = DatabaseConstant.COLUMN(DatabaseConstant.DATETIME, default=db.func.current_timestamp(),
                                         nullable=False)
    updated_at = DatabaseConstant.COLUMN(DatabaseConstant.DATETIME, nullable=True,
                                         default=db.func.current_timestamp())

    @staticmethod
    def _cast_value_to_type(value, datatype):
        if datatype == 'int':
            return int(value)
        elif datatype == 'float':
            return float(value)
        elif datatype == 'boolean':
            if isinstance(value, bool):
                return value
            if isinstance(value, int):
                return bool(value)
            val = str(value).strip().lower()
            if val in ['1', 'true', 'yes', 'on']:
                return True
            elif val in ['0', 'false', 'no', 'off']:
                return False
            else:
                raise ValueError(f'Cannot cast {value} to boolean')
        else:
            return str(value)

    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key, cast to its datatype if found."""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            try:
                return cls._cast_value_to_type(setting.value, setting.datatype)
            except Exception:
                return default
        return default

    @classmethod
    def set_setting(cls, key, value, description=None):
        """Set a setting value by key, enforcing the datatype."""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            # Ensure value can be cast to the correct type before saving
            casted = cls._cast_value_to_type(value, setting.datatype)
            setting.value = str(casted)
            if description:
                setting.description = description
        else:
            # Require datatype for new settings
            raise ValueError('Datatype must be set when creating a new setting')
        db.session.commit()
        return setting

    @classmethod
    def create_setting(cls, key, value, datatype, description=None):
        """Create a new setting, enforcing the datatype."""
        # Ensure value can be cast to the correct type before saving
        casted = cls._cast_value_to_type(value, datatype)
        setting = cls(key=key, value=str(casted), datatype=datatype, description=description)
        db.session.add(setting)
        db.session.commit()
        return setting