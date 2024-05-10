
# Discord-Integrated Wake-on-LAN Application

This Flask application allows authorized Discord users to remotely wake a computer over the network. It utilizes Discord OAuth for authentication and checks user roles within a specified guild (Discord server) to determine if the user has the required permissions to initiate a Wake-on-LAN (WOL) signal.

## Features

- **Discord OAuth Integration**: Users must authenticate via Discord to access the Wake-on-LAN feature.
- **Role Verification**: Only users with a specified role within the Discord guild can trigger the WOL.
- **Logging**: Detailed logging of operations and errors.
- **Security**: Uses environment variables to manage sensitive information securely.

## Requirements

- Python 3.x
- Flask
- Flask-Dance
- Requests
- Wakeonlan
- A Discord application with a bot and OAuth2 setup

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine or server where you intend to run the application.

```bash
git clone <repository-url>
```

### 2. Install Dependencies

Navigate into the project directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root of your project directory and update it with your specific values:

```plaintext
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_discord_guild_id
REQUIRED_ROLE_ID=your_required_role_id
WOL_MAC_ADDRESS=your_target_mac_address
WOL_IP_ADDRESS=your_target_ip_address
WOL_PORT=your_target_port
APP_PORT=5000  # or any other port you prefer
SECRET_KEY=your_secret_key_for_flask_session
```

### 4. Configure Discord

Ensure your Discord app is properly configured with the necessary OAuth2 scopes (`identify`, `guilds`) and bot permissions to read guild and role information.

### 5. Run the Application

Start the server using:

```bash
python server.py
```

Navigate to `http://localhost:5000` (or whichever port you set) on your web browser to access the application.

## Usage

Once the application is running:

1. Authenticate via Discord by following the on-screen prompts.
2. If authenticated and authorized (based on role verification), you will be able to trigger the Wake-on-LAN to wake up the specified machine.

## Logs

Check `app.log` for detailed operation logs and troubleshooting.

## Contributing

Contributions are welcome. Please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
