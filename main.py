from app import create_app
from app.config import Config, config_dict

app_config = config_dict['Debug'] if Config.DEBUG else config_dict['Production']

app = create_app(app_config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)