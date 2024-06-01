import discord
import pandas as pd
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load values from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CONFIGURED_ROLES = os.getenv('CONFIGURED_ROLES').split(',')
AUTHORIZED_ROLES = [int(role_id) for role_id in os.getenv('AUTHORIZED_ROLES').split(',')]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Convert CONFIGURED_ROLES to a set for faster lookup
CONFIGURED_ROLES = set(CONFIGURED_ROLES)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='ranks')
@commands.has_any_role(*AUTHORIZED_ROLES)
async def ranks(ctx, role_id: int):
    # Get the role object
    role = ctx.guild.get_role(role_id)
    if role is None:
        await ctx.send("Role not found.")
        return

    # Iterate through members with the given role
    results = []
    for member in role.members:
        # Check for configured roles
        found_roles = [r.name for r in member.roles if r.name in CONFIGURED_ROLES]
        if found_roles:
            for fr in found_roles:
                results.append([member.id, fr])
        else:
            results.append([member.id, "not found"])

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(results, columns=["UserID", "RoleName"])
    df.to_csv("role_check_results.csv", index=False)

    # Inform the user and send the file
    await ctx.send(file=discord.File("role_check_results.csv"))

# Run the bot
bot.run(TOKEN)