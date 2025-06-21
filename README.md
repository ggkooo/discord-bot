# Discord Bot

This is a complete Discord bot for server management, ticketing, moderation, and logging, built with [discord.py](https://discordpy.readthedocs.io/).  
It is designed for stores, communities, and support servers, with advanced features such as ticket creation, logging of user actions, and administrative commands.

---

## 📥 Download

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ggkooo/discord-bot.git
   cd discord-bot
   ```

2. **Or download the ZIP:**
   - Click on "Code" > "Download ZIP" and extract it to your desired folder.

---

## ⚙️ Installation

1. **Install Python 3.10+**  
   Download from [python.org](https://www.python.org/downloads/).

2. **(Optional) Create a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

---

## 🔑 Environment Variables

1. **Copy the example file:**
   ```sh
   cp .env.example .env
   ```
   Or manually create a `.env` file in the project root.

2. **Edit `.env` and fill in your values:**

   ```
   DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE

   # ROLES
   ADMIN_ROLE_ID=YOUR_ADMIN_ROLE_ID
   SUPPORT_ROLE_ID=YOUR_SUPPORT_ROLE_ID

   # CHANNELS
   TRANSCRIPT_CHANNEL_ID=YOUR_TRANSCRIPT_CHANNEL_ID
   ZIP_CHANNEL_ID=YOUR_ZIP_CHANNEL_ID
   JOIN_CHANNEL_ID=YOUR_JOIN_CHANNEL_ID
   LEAVE_CHANNEL_ID=YOUR_LEAVE_CHANNEL_ID
   ANTI_CHANNEL_ID=YOUR_ANTI_CHANNEL_ID
   ```

   - **DISCORD_TOKEN:** Your bot token from the [Discord Developer Portal](https://discord.com/developers/applications).
   - **ROLE IDs:** Get these by right-clicking the role in Discord (developer mode enabled) and clicking "Copy ID".
   - **CHANNEL IDs:** Right-click the channel and "Copy ID".

---

## 🚀 Running the Bot

```sh
python main.py
```

If everything is set up correctly, you will see a message like:
```
Logged in as SpectreBot (ID: 123456789012345678)
```

---

## 🛠️ Main Features

### 🎫 Ticket System
- Users can open tickets for support, purchases, or questions.
- Tickets are created in dedicated channels with restricted access.
- Staff and admins can manage tickets, close them, and send reminders.

### 📝 Logging
- **Member Join:** Logs when a user joins the server in a specific channel.
- **Member Leave:** Logs when a user leaves the server in another channel.
- **Message Edit/Delete:** Logs edited and deleted messages in a log channel, with full embed details.
- **Ban Command:** Admins can ban users by ID, selecting a reason from a dropdown.

### 🛡️ Moderation
- `/ban <user_id>`: Ban a user by ID, with a reason selector.
- `/clear`: Bulk delete messages in a channel.

### 🔔 Notifications
- Private reminders for ticket owners.
- Custom embeds for all logs and notifications.

---

## 📚 Example: Channel and Role Setup

Below are example images and IDs for your `.env` file.  
**Replace these with your actual server/channel/role IDs.**

### Example Roles

| Role Name      | Example ID           |
|----------------|---------------------|
| Admin          | 1241829059617619988 |
| Support        | 1241829061324574791 |

### Example Channels

| Channel Purpose      | Example ID           |
|---------------------|---------------------|
| Transcript Channel  | 1241829321883127828 |
| ZIP Channel         | 1385776264912044213 |
| Member Join Log     | 1241829326517833889 |
| Member Leave Log    | 1241829330066214912 |
| Anti-Log Channel    | 1265182908981706802 |

> **Tip:** To get the ID of a channel or role, enable Developer Mode in Discord (Settings > Advanced > Developer Mode), then right-click the channel/role and select "Copy ID".

---

## ❓ FAQ

- **Q:** My bot doesn't start or gives "Improper token has been passed."  
  **A:** Double-check your `.env` file and make sure your bot token is correct and active.

- **Q:** How do I get channel or role IDs?  
  **A:** Enable Developer Mode in Discord, right-click the channel/role, and select "Copy ID".

- **Q:** How do I add the bot to my server?  
  **A:** Use the OAuth2 URL Generator in the Discord Developer Portal, select "bot" and the required permissions, and invite the bot.

---

## 🤝 Contributing

Pull requests and suggestions are welcome!  
Open an issue or PR to discuss improvements or report bugs.

---

## 📄 License

This project is licensed under the MIT License.

---

**Discord Bot**  
Made with ❤️ using [discord.py](https://discordpy.readthedocs.io/)