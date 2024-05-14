import aiosqlite
import discord

from discord import app_commands, utils
from discord.ext import commands

from views.ticket.ticket_views import TicketOpenedView, TicketSetupView, ConfirmCloseView, ConfirmArchiveView

import datetime
import os

from dotenv import load_dotenv

load_dotenv()

ticket_viewer_roles = [
    1233379649418035221
]

open_tickets = {}

TOKEN = os.getenv('TICKET_BOT_TOKEN')

ticket_category_id = int(os.getenv('TICKET_CATEGORY_ID'))
ticket_archive_category_id = int(os.getenv('TICKET_ARCHIVE_CATEGORY_ID'))

log_channel_id = int(os.getenv('LOG_CHANNEL_ID'))


async def remove_channel_permissions(channel, member_id):
    member = channel.guild.get_member(member_id)

    if member is not None:
        await channel.send(f'{member.mention}')
        await channel.set_permissions(member, overwrite=None)


class NovaClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)

        self.synced = False
        self.added = False

    async def on_ready(self):
        await self.wait_until_ready()

        if not self.synced:
            await tree.sync()
            self.synced = True

        if not self.added:
            self.add_view(TicketSetupView())
            self.add_view(TicketOpenedView())
            self.added = True

        await self.change_presence(activity=discord.Game(name='Clash of Clans'), status=discord.Status.dnd)

        print(f'Bot is ready')


client = NovaClient()
tree = app_commands.CommandTree(client)


@tree.command(name='setup', description='Sets up the ticket message')
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def ticket_setup(interaction: discord.Interaction):
    embed = discord.Embed(title='Nova Clan Application & Support', description='__Thank you for your interest in the **Nova Family**__\n\n'
                                                                'Create a ticket if you are interested in joining one of our clans, or require assistance from a member of staff.\n\n'
                                                                '**Application Process**\n'
                                                                '> <:bulletpoint:1237033867785932890> Questions: respond to a few short questions.\n'
                                                                '> <:bulletpoint:1237033867785932890> Interview: Q&A to determine your play style, '
                                                                'and find the right spot for you in one of our clans.\n'
                                                                '> <:bulletpoint:1237033867785932890> Acceptance: official welcome and a brief trial period to show your skills.')

    embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
    embed.timestamp = datetime.datetime.now()

    await interaction.channel.send(embed=embed, view=TicketSetupView())
    await interaction.response.send_message('Ticket system is set up.', ephemeral=True, delete_after=5)


@tree.command(name='close', description='Closes desired ticket')
@app_commands.checks.has_permissions(administrator=True)
async def ticket_close(interaction: discord.Interaction):
    if not 'ticket-' in interaction.channel.name:
        return await interaction.response.send_message('This channel is not a ticket', ephemeral=True, delete_after=3)

    embed = discord.Embed(title='Close ticket', description='Are you sure you want to close this ticket?',
                          color=discord.Color.blurple())

    embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
    embed.timestamp = datetime.datetime.now()

    await interaction.response.send_message(embed=embed, view=ConfirmCloseView(), ephemeral=True)


@tree.command(name='archive', description='Archives desired ticket')
@app_commands.checks.has_permissions(administrator=True)
async def ticket_archive(interaction: discord.Interaction):
    if not 'ticket-' in interaction.channel.name:
        return await interaction.response.send_message('This channel is not a ticket', ephemeral=True, delete_after=3)

    if 'archived-' in interaction.channel.name:
        return await interaction.response.send_message('This ticket is already archived', ephemeral=True,
                                                       delete_after=3)

    embed = discord.Embed(title='Archive ticket', description='📝 Are you sure you want to archive this ticket?',
                          color=discord.Color.blurple())

    embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
    embed.timestamp = datetime.datetime.now()

    await interaction.response.send_message(embed=embed, view=ConfirmArchiveView(), ephemeral=True)


@tree.command(name='add', description='Adds a member to desired ticket')
@app_commands.describe(member='Member you want to add')
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def ticket_add(interaction: discord.Interaction, member: discord.Member):
    if not 'ticket-' in interaction.channel.name:
        return await interaction.response.send_message('This channel is not a ticket', ephemeral=True, delete_after=3)

    await interaction.channel.set_permissions(member,
                                              view_channel=True,
                                              send_messages=True,
                                              read_message_history=True,
                                              attach_files=True,
                                              embed_links=True)

    await interaction.response.send_message(
        f'> {member.mention} got added to this ticket by {interaction.user.mention}')


@tree.command(name='remove', description='Removes a member of desired ticket')
@app_commands.describe(member='Member you want to remove')
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def ticket_remove(interaction: discord.Interaction, member: discord.Member):
    if not 'ticket-' in interaction.channel.name:
        return await interaction.response.send_message('This channel is not a ticket', ephemeral=True, delete_after=3)

    if member.top_role.id in ticket_viewer_roles:
        return await interaction.response.send_message(f'{member.mention} has a ticket viewer role, therefore he '
                                                       f'can not be removed from this ticket.', ephemeral=True)

    await interaction.channel.set_permissions(member, overwrite=None)
    await interaction.response.send_message(
        f'> {member.mention} got removed from this ticket by {interaction.user.mention}')


@tree.context_menu(name='Open a ticket')
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def open_ticket_context_menu(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)

    ticket_channel = utils.get(interaction.guild.text_channels, name=f'ticket-'
                                                                     f"{member.name.lower().replace(' ', '-')}-"
                                                                     f'{member.discriminator}')

    if ticket_channel is not None:
        return await interaction.followup.send(f'{member.mention} already has a ticket at {ticket_channel.mention}',
                                               ephemeral=True)

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True,
                                                      read_message_history=True,
                                                      send_messages=True,
                                                      attach_files=True,
                                                      embed_links=True),
        interaction.guild.me: discord.PermissionOverwrite(view_channel=True,
                                                          read_message_history=True,
                                                          send_messages=True),
    }

    for ticket_viewer_role in ticket_viewer_roles:
        role = interaction.guild.get_role(ticket_viewer_role)

        if not role:
            continue

        overwrites.update({
            role: discord.PermissionOverwrite(view_channel=True,
                                              read_message_history=True,
                                              send_messages=True,
                                              attach_files=True,
                                              embed_links=True),
        })

    try:
        category = utils.get(interaction.guild.categories, id=ticket_category_id)

        channel = await interaction.guild.create_text_channel(name=f'ticket-{member.name}-'
                                                                   f'{member.discriminator}',
                                                              category=category,
                                                              overwrites=overwrites)
    except:
        return await interaction.response.send_message(f'Ticket creation failed, '
                                                       f'make sure this bot has enough permissions to create channels',
                                                       ephemeral=True,
                                                       delete_after=5)

    await channel.send(f'@here\nA ticket for {member.mention} got opened by {interaction.user.mention}',
                       view=TicketOpenedView())
    await interaction.followup.send(f'A ticket got created for {member.mention} in {channel.mention}', ephemeral=True)


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.BotMissingPermissions):
        return await interaction.response.send_message(error, ephemeral=True)
    else:
        await interaction.response.send_message('An unknown error occured', ephemeral=True)
        raise error


client.run(TOKEN)
