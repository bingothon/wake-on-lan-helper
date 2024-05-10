import os
import logging
from logging.handlers import RotatingFileHandler
import socket
from flask import Flask, redirect, url_for, session, render_template, jsonify
from flask_dance.contrib.discord import make_discord_blueprint, discord
from dotenv import load_dotenv
from wakeonlan import send_magic_packet
import requests

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development on HTTP
load_dotenv()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[RotatingFileHandler('app.log', maxBytes=5*1024*1024, backupCount=2), logging.StreamHandler()])
logging.captureWarnings(True)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

discord_blueprint = make_discord_blueprint(
    client_id=os.getenv('DISCORD_CLIENT_ID'),
    client_secret=os.getenv('DISCORD_CLIENT_SECRET'),
    redirect_to='wakeup',
    scope=["identify", "guilds"] 
)
app.register_blueprint(discord_blueprint, url_prefix='/login')

def send_tcp_command(ip, port, message, timeout=10):  # Added a default timeout parameter
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)  # Set the timeout for the connection
            sock.connect((ip, int(port)))
            sock.sendall(message.encode())
            # If you need to wait for a response, uncomment the next lines:
            # response = sock.recv(1024)
            # return response.decode()
            return "Success"
    except socket.timeout:
        logging.error(f"Connection timed out: Could not connect to {ip}:{port}")
        return "Timeout"
    except socket.error as e:
        logging.error(f"Socket error: {e}")
        return "Socket Error"

def get_user_roles(guild_id, user_id, bot_token):
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
    headers = {"Authorization": f"Bot {bot_token}"}
    response = requests.get(url, headers=headers)
    response_data = response.json()  # Get the JSON response data

    # Log the response data to debug
    logging.debug(f"API Response: {response_data}")

    if response.status_code == 200:
        # Directly return the list of role IDs, which are already in the correct format
        return response_data.get('roles', [])  # This will return an empty list if 'roles' is not found
    else:
        # Log any non-200 responses
        logging.error(f"Failed to fetch roles with status code {response.status_code}, response: {response_data}")
        return []


def user_has_role(user_roles, required_role_id):
    return required_role_id in user_roles

@app.route('/')
def index():
    if not discord.authorized:
        return redirect(url_for('discord.login'))
    return redirect(url_for('wakeup'))

@app.route('/wakeup')
def wakeup():
    if not discord.authorized:
        return redirect(url_for('discord.login'))

    discord_guild_id = os.getenv('DISCORD_GUILD_ID')
    required_role_id = os.getenv('REQUIRED_ROLE_ID')
    bot_token = os.getenv('DISCORD_BOT_TOKEN')  # Ensure you have this in your environment variables
    user_info = discord.get('/api/users/@me').json()

    roles = get_user_roles(discord_guild_id, user_info["id"], bot_token)

    if not user_has_role(roles, required_role_id):
        logging.warning(f"User {user_info['username']} does not have the required role. Roles: {roles}")
        return jsonify({"error": "You do not have permission to perform this action"}), 403

    username = user_info['username']
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png"
    wol_mac_address = os.getenv('WOL_MAC_ADDRESS')
    wol_ip_address = os.getenv('WOL_IP_ADDRESS')
    wol_port = os.getenv('WOL_PORT')
    
    if wol_mac_address and wol_ip_address and wol_port:
        send_magic_packet(wol_mac_address, ip_address=wol_ip_address, port=int(wol_port))
        logging.info(f"{username} triggered Wake on LAN successfully.")
        return render_template('./countdown.html', username=username, avatar_url=avatar_url), 200
    else:
        logging.error("Failed to retrieve environment settings.")
        return 'Environment configuration error. Please check settings.', 500
    
@app.route('/sleep', methods=['POST'])    
def sleep():
    if not discord.authorized:
        return jsonify({"error": "Unauthorized access"}), 401

    discord_guild_id = os.getenv('DISCORD_GUILD_ID')
    required_role_id = os.getenv('REQUIRED_ROLE_ID')
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    user_info = discord.get('/api/users/@me').json()

    roles = get_user_roles(discord_guild_id, user_info["id"], bot_token)

    if not user_has_role(roles, required_role_id):
        logging.warning(f"User {user_info['username']} does not have the required role. Roles: {roles}")
        return jsonify({"error": "You do not have permission to perform this action"}), 403

    sleep_ip_address = os.getenv('WOL_IP_ADDRESS')
    client_port = os.getenv('CLIENT_PORT')
    sleep_message = "sleep:" + os.getenv('SECRET_KEY')

    if sleep_ip_address and client_port:
        result = send_tcp_command(sleep_ip_address, client_port, sleep_message)
        if result is not None:
            logging.info(f"Sleep command triggered successfully by {user_info['username']}.")
            return jsonify({"status": "Sleep command sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send sleep command"}), 500
    else:
        logging.error("Required IP address or port not provided.")
        return jsonify({"error": "Configuration error. Please check settings."}), 500

if __name__ == '__main__':
    app.run(port=os.getenv('APP_PORT'), debug=True)
