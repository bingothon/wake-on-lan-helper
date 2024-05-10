import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for, session, render_template_string
from flask_dance.contrib.discord import make_discord_blueprint, discord
from dotenv import load_dotenv
from wakeonlan import send_magic_packet

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development on HTTP
load_dotenv()

# Configure logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log_file_handler = RotatingFileHandler('app.log', mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
log_file_handler.setFormatter(log_formatter)
log_file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[log_file_handler, stream_handler])
logging.captureWarnings(True)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

discord_blueprint = make_discord_blueprint(
    client_id=os.getenv('DISCORD_CLIENT_ID'),
    client_secret=os.getenv('DISCORD_CLIENT_SECRET'),
    redirect_to='wakeup',
    scope=["identify"]
)
app.register_blueprint(discord_blueprint, url_prefix='/login')

@app.route('/')
def index():
    logging.info("Navigating to index page, checking authorization.")
    if not discord.authorized:
        logging.warning("User not authorized, redirecting to login.")
        return redirect(url_for('discord.login'))
    return redirect(url_for('wakeup'))

@app.route('/wakeup')
def wakeup():
    logging.info("User accessed the wakeup route.")
    if not discord.authorized:
        logging.error("Unauthorized access attempted on wakeup.")
        return redirect(url_for('discord.login'))

    user_info = discord.get('/api/users/@me').json()
    username = user_info['username']
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png"

    wol_mac_address = os.getenv('MAC_ADDRESS')
    wol_ip_address = os.getenv('IP_ADDRESS')
    wol_port = os.getenv('PORT')
    
    if wol_mac_address and wol_ip_address and wol_port:
        logging.debug(f"Sending magic packet to MAC: {wol_mac_address}, IP: {wol_ip_address}, PORT: {wol_port}")
        send_magic_packet(wol_mac_address, ip_address=wol_ip_address, port=int(wol_port))

        logging.info(f"{username} triggered Wake on LAN successfully.")
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Countdown</title>
            <style>
                body {{ font-family: Arial, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background-color: #f0f0f0; }}
                img {{ border-radius: 50%; }}
                .countdown {{ font-size: 2em; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <h1>Hello, {username}!</h1>
            <img src="{avatar_url}" alt="User avatar" width="100">
            <div class="countdown">Stream PC will be available in <span id="time">30</span> seconds.</div>
            <script>
                var time = 30;
                var intervalId = setInterval(function() {{
                    time--;
                    document.getElementById('time').textContent = time;
                    if (time <= 0) {{
                        clearInterval(intervalId);
                        document.querySelector('.countdown').textContent = 'Stream PC should be available now!';
                    }}
                }}, 1000);
            </script>
        </body>
        </html>
        """
        return render_template_string(html), 200
    else:
        logging.error("Failed to retrieve environment settings.")
        return 'Environment configuration error. Please check settings.', 500

if __name__ == '__main__':
    app.run(port=12345, debug=True)
