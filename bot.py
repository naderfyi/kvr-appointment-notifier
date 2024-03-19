import os
from dotenv import load_dotenv
import nextcord
from nextcord.ext import tasks
from munich_KVR_bot import kvr_bot

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = nextcord.Intents.all()
intents.members = True
bot = nextcord.Client(intents=intents)

@bot.event
async def on_ready():
    """Print a message to the console when the bot is ready."""
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    print("------")
    
    # Start the background task
    check_appointments.start()

def get_date_interval(date_list):
    """Retrieve the interval of checked dates."""
    if date_list:
        min_date = min(date_list)
        max_date = max(date_list)
        return f"{min_date.strftime('%d %b %Y')} - {max_date.strftime('%d %b %Y')}"
    return "No date range available"

def format_appointments(appointments):
    """Formats the dates for better readability in the message."""
    # Join the dates, each on a new line.
    return '\n'.join([appointment.strftime('%d %b %Y') for appointment in appointments])

@tasks.loop(minutes=5)
async def check_appointments():
    """Checks for appointments and sends an embed with the details to the Discord channel."""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Channel {CHANNEL_ID} not found.")
        return

    try:
        # Get data from the website
        date_list_df, appointments = kvr_bot()

        # If abh_bot returns a DataFrame, we convert the relevant column to a list
        date_list = date_list_df['date'].tolist() if not date_list_df.empty else []

        date_interval = get_date_interval(date_list)

        # Create an embed object
        embed_color = 0x00FF00 if appointments else 0xFF0000  # Green if appointments are available, else red
        embed = nextcord.Embed(title="📅 Appointment Availability Status", color=embed_color)
        embed.add_field(name="Checked Dates", value=f"{date_interval}", inline=False)

        # Define the message content and embed based on the availability of appointments
        if appointments:
            appointments_str = format_appointments(appointments)
            embed.add_field(name="Available Appointments", value=appointments_str, inline=False)
            # link to website
            embed.add_field(name="Book Here", value=os.getenv("BASE_URL"), inline=False)
            embed.set_footer(text="Hurry up and book your appointment!")
            message_content = "@everyone\n"  # This will mention everyone in the message
        else:
            embed.add_field(name="Available Appointments", value="No appointments available at this time.", inline=False)
            embed.set_footer(text="Keep trying!")
            message_content = ""  # No need to mention everyone if there are no appointments

        # Send the message and embed to the channel
        await channel.send(content=message_content, embed=embed)

    except Exception as e:
        print(f"An error occurred: {e}")
        error_embed = nextcord.Embed(
            title="⚠ Error",
            description="An error occurred while checking for appointments.",
            color=0xFF0000  # Red color for errors
        )
        await channel.send(embed=error_embed)

bot.run(DISCORD_TOKEN)
