import aiosqlite
import discord

from discord import utils
from discord.ext import commands

import datetime
import os

from dotenv import load_dotenv

load_dotenv()

ticket_viewer_roles = [
    1236984104206073896
]

ticket_category_id = int(os.getenv('TICKET_CATEGORY_ID'))
ticket_archive_category_id = int(os.getenv('TICKET_ARCHIVE_CATEGORY_ID'))

log_channel_id = int(os.getenv('LOG_CHANNEL_ID'))


class TicketSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.member)

    @discord.ui.button(label='Apply',
                       style=discord.ButtonStyle.blurple,
                       custom_id='ticket_create_apply_button',
                       emoji='📑')
    async def ticket_create_apply(self, interaction: discord.Interaction, button: discord.ui.Button):
        interaction.message.author = interaction.user
        retry = self.cooldown.get_bucket(interaction.message).update_rate_limit()

        if retry:
            return await interaction.response.send_message(f'You currently are on cooldown.\n'
                                                           f'Try again in {round(retry, 1)} seconds',
                                                           ephemeral=True,
                                                           delete_after=5)

        ticket_channel = utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")

        if ticket_channel is not None:
            return await interaction.response.send_message(f'You already have a ticket in {ticket_channel.mention}',
                                                           ephemeral=True,
                                                           delete_after=5)

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

            channel = await interaction.guild.create_text_channel(name=f'ticket-{interaction.user.name}-'
                                                                       f'{interaction.user.discriminator}',
                                                                  category=category,
                                                                  overwrites=overwrites)
        except:
            return await interaction.response.send_message(f'Ticket creation failed, '
                                                           f'make sure this bot has enough permissions to create channels',
                                                           ephemeral=True,
                                                           delete_after=5)

        embed = discord.Embed(title=f'{interaction.user} opened an application ticket',
                              description=f'The Staff team is already contacted\nIn the meantime, you can already go ahead and post your player-tag in here to fasten the process.')

        if interaction.user.display_icon:
            embed.set_thumbnail(url=interaction.user.display_icon)

        embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
        embed.timestamp = datetime.datetime.now()

        mentions = ''

        for ticket_viewer_role in ticket_viewer_roles:
            role = interaction.guild.get_role(ticket_viewer_role)

            if role:
                mentions += f'{role.mention} '

        await channel.send(mentions, embed=embed, view=TicketOpenedView())

        await interaction.response.send_message(f'A ticket got created for you in {channel.mention}', ephemeral=True)

        log_channel = interaction.guild.get_channel(log_channel_id)

        if log_channel:
            embed = discord.Embed(title='Application Ticket opened | 📑',
                                  description=f'{interaction.user.mention} opened an application ticket in {channel.mention}',
                                  color=discord.Color.blurple())

            if interaction.user.display_icon:
                embed.set_thumbnail(url=interaction.user.display_icon)

            embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
            embed.timestamp = datetime.datetime.now()

            await log_channel.send(embed=embed)

        async with aiosqlite.connect('database/open_tickets.db') as db:
            await db.execute('CREATE TABLE IF NOT EXISTS members (member_id INTEGER, channel_id INTEGER)')
            await db.commit()

            await db.execute('INSERT INTO members (member_id, channel_id) VALUES (?, ?)', (interaction.user.id,
                                                                                           channel.id))
            await db.commit()


    @discord.ui.button(label='Support',
                       style=discord.ButtonStyle.red,
                       custom_id='ticket_create_support_button',
                       emoji='📩')
    async def ticket_create(self, interaction: discord.Interaction, button: discord.ui.Button):
        interaction.message.author = interaction.user
        retry = self.cooldown.get_bucket(interaction.message).update_rate_limit()

        if retry:
            return await interaction.response.send_message(f'You currently are on cooldown.\n'
                                                           f'Try again in {round(retry, 1)} seconds',
                                                           ephemeral=True,
                                                           delete_after=5)

        ticket_channel = utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")

        if ticket_channel is not None:
            return await interaction.response.send_message(f'You already have a ticket in {ticket_channel.mention}',
                                                           ephemeral=True,
                                                           delete_after=5)

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

            channel = await interaction.guild.create_text_channel(name=f'ticket-{interaction.user.name}-'
                                                                       f'{interaction.user.discriminator}',
                                                                  category=category,
                                                                  overwrites=overwrites)
        except:
            return await interaction.response.send_message(f'Ticket creation failed, '
                                                           f'make sure this bot has enough permissions to create channels',
                                                           ephemeral=True,
                                                           delete_after=5)

        embed = discord.Embed(title=f'{interaction.user} opened a support ticket',
                              description=f'The Staff team is already contacted\n'
                                           'Feel free to ask your question in here')

        if interaction.user.display_icon:
            embed.set_thumbnail(url=interaction.user.display_icon)

        embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
        embed.timestamp = datetime.datetime.now()

        mentions = ''

        for ticket_viewer_role in ticket_viewer_roles:
            role = interaction.guild.get_role(ticket_viewer_role)

            if role:
                mentions += f'{role.mention} '

        await channel.send(mentions, embed=embed, view=TicketOpenedView())

        await interaction.response.send_message(f'A ticket got created for you in {channel.mention}', ephemeral=True)

        log_channel = interaction.guild.get_channel(log_channel_id)

        if log_channel:
            embed = discord.Embed(title='Ticket opened | 📩',
                                  description=f'{interaction.user.mention} opened a support ticket in {channel.mention}',
                                  color=discord.Color.blurple())

            if interaction.user.display_icon:
                embed.set_thumbnail(url=interaction.user.display_icon)

            embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
            embed.timestamp = datetime.datetime.now()

            await log_channel.send(embed=embed)

        async with aiosqlite.connect('database/open_tickets.db') as db:
            await db.execute('CREATE TABLE IF NOT EXISTS members (member_id INTEGER, channel_id INTEGER)')
            await db.commit()

            await db.execute('INSERT INTO members (member_id, channel_id) VALUES (?, ?)', (interaction.user.id,
                                                                                           channel.id))
            await db.commit()

    @discord.ui.button(label='Something Else',
                       custom_id='ticket_create_others_button',
                       emoji='📝')
    async def ticket_create_others(self, interaction: discord.Interaction, button: discord.ui.Button):
        interaction.message.author = interaction.user
        retry = self.cooldown.get_bucket(interaction.message).update_rate_limit()

        if retry:
            return await interaction.response.send_message(f'You currently are on cooldown.\n'
                                                           f'Try again in {round(retry, 1)} seconds',
                                                           ephemeral=True,
                                                           delete_after=5)

        ticket_channel = utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")

        if ticket_channel is not None:
            return await interaction.response.send_message(f'You already have a ticket in {ticket_channel.mention}',
                                                           ephemeral=True,
                                                           delete_after=5)

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

            channel = await interaction.guild.create_text_channel(name=f'ticket-{interaction.user.name}-'
                                                                       f'{interaction.user.discriminator}',
                                                                  category=category,
                                                                  overwrites=overwrites)
        except:
            return await interaction.response.send_message(f'Ticket creation failed, '
                                                           f'make sure this bot has enough permissions to create channels',
                                                           ephemeral=True,
                                                           delete_after=5)

        embed = discord.Embed(title=f'{interaction.user} opened an others ticket',
                              description=f'The Staff team is already contacted\nFeel free to ask your question in here and we will answer you shortly.')

        if interaction.user.display_icon:
            embed.set_thumbnail(url=interaction.user.display_icon)

        embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
        embed.timestamp = datetime.datetime.now()

        mentions = ''

        for ticket_viewer_role in ticket_viewer_roles:
            role = interaction.guild.get_role(ticket_viewer_role)

            if role:
                mentions += f'{role.mention} '

        await channel.send(mentions, embed=embed, view=TicketOpenedView())

        await interaction.response.send_message(f'A ticket got created for you in {channel.mention}', ephemeral=True)

        log_channel = interaction.guild.get_channel(log_channel_id)

        if log_channel:
            embed = discord.Embed(title='Others Ticket opened | 📝',
                                  description=f'{interaction.user.mention} opened an others ticket in {channel.mention}',
                                  color=discord.Color.blurple())

            if interaction.user.display_icon:
                embed.set_thumbnail(url=interaction.user.display_icon)

            embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
            embed.timestamp = datetime.datetime.now()

            await log_channel.send(embed=embed)

        async with aiosqlite.connect('database/open_tickets.db') as db:
            await db.execute('CREATE TABLE IF NOT EXISTS members (member_id INTEGER, channel_id INTEGER)')
            await db.commit()

            await db.execute('INSERT INTO members (member_id, channel_id) VALUES (?, ?)', (interaction.user.id,
                                                                                           channel.id))
            await db.commit()


class TicketOpenedView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Close ticket', style=discord.ButtonStyle.red, custom_id='close_ticket', emoji='🔐')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title='Close ticket', description='🔐 Are you sure you want to close this ticket?',
                              color=discord.Color.blurple())

        embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
        embed.timestamp = datetime.datetime.now()

        await interaction.response.send_message(embed=embed, view=ConfirmCloseView(), ephemeral=True)

    @discord.ui.button(label='Archive ticket', style=discord.ButtonStyle.blurple, custom_id='archive_ticket', emoji='📝')
    async def archive_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(title='Archive ticket', description='📝 Are you sure you want to archive this ticket?',
                                  color=discord.Color.blurple())

            embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
            embed.timestamp = datetime.datetime.now()

            await interaction.response.send_message(embed=embed, view=ConfirmArchiveView(), ephemeral=True)

            return

        await interaction.response.send_message(f'You do not have the permissions to archive this ticket', ephemeral=True)


class ConfirmArchiveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Confirm archiving', style=discord.ButtonStyle.red, custom_id='archive_ticket_confirm',
                       emoji='📝')
    async def confirm_archive_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.top_role.id not in ticket_viewer_roles:
            return await interaction.response.send_message(f'You do not have the permission to archive this ticket!', ephemeral=True)

        if interaction.channel.name.startswith('archived-'):
            return await interaction.response.send_message(f'This ticket is already archived', ephemeral=True)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
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

        category = utils.get(interaction.guild.categories, id=ticket_archive_category_id)

        try:
            old_channel_name = interaction.channel.name

            new_channel_name = f'archived-{old_channel_name}'

            await interaction.channel.edit(category=category, name=new_channel_name, overwrites=overwrites)

            await interaction.response.send_message(f'This channel got archived at: '
                                                    f'{datetime.datetime.now()} by {interaction.user.mention}')

            log_channel = interaction.guild.get_channel(log_channel_id)

            if log_channel:
                embed = discord.Embed(title='Ticket archived | 📩',
                                      description=f'{interaction.user.mention} has archived the ticket `{old_channel_name}`',
                                      color=discord.Color.blurple())

                if interaction.user.display_icon:
                    embed.set_thumbnail(url=interaction.user.display_icon)

                embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
                embed.timestamp = datetime.datetime.now()

                await log_channel.send(embed=embed)
        except:
            await interaction.response.send_message(f'Channel archiving failed', ephemeral=True)


class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Confirm closing', style=discord.ButtonStyle.red, custom_id='close_ticket_confirm',
                       emoji='🔐')
    async def confirm_close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.top_role.id not in ticket_viewer_roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(f'You do not have the permissions to close this ticket!', ephemeral=True)

        try:
            channel_id = interaction.channel.id
            channel_name = interaction.channel.name

            await interaction.channel.delete()

            log_channel = interaction.guild.get_channel(log_channel_id)

            if log_channel:
                embed = discord.Embed(title='Ticket closed | 📩',
                                      description=f'{interaction.user.mention} has closed the ticket `{channel_name}`',
                                      color=discord.Color.blurple())

                if interaction.user.display_icon:
                    embed.set_thumbnail(url=interaction.user.display_icon)

                embed.set_footer(text='Created by Nova6 Team', icon_url=interaction.guild.icon)
                embed.timestamp = datetime.datetime.now()

                await log_channel.send(embed=embed)

            async with aiosqlite.connect('database/open_tickets.db') as db:
                await db.execute('DELETE FROM members WHERE channel_id = ?', [(channel_id)])

                await db.commit()
        except:
            await interaction.response.send_message(f'Channel deletion failed', ephemeral=True)
