import discord
from discord.ext import commands
from discord import app_commands
import json
import re
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ui import View , Button
from utils import bot_instance, ids
from collections import defaultdict



bot = bot_instance.instance


spotify_url_regex = re.compile(r'https?://open\.spotify\.com/(track|playlist)/([^?]+)')
youtube_url_regex = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/')

client_credentials_manager = SpotifyClientCredentials(client_id='0df62a61d2334fd49ab6696d6c2a3ad1', client_secret='8998e81039d842f5ab02482071627bd5')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

recommendation_channel_id = 1385387123053564004 #ids.recommendation_channel_id
my_guild_id = ids.my_guild_id

# data_dir = "/home/container/cogs/musicrec"
data_dir = "cogs/musicrec"


queue_file = os.path.join(data_dir,"recommendations_data.json")
all_songs_file = os.path.join(data_dir,"all_songs.json")
user_songs_file = os.path.join(data_dir,"user_songs.json")

#----------------------- DATA HANDLING ----------------------------------------    

def load_data(file, default):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default

def save_data(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


def load_queue():
    return load_data(queue_file, [])

def save_queue(queue):
    queue = rearrange_queue(queue)
    save_data(queue, queue_file)

def save_to_all_songs(track_id, track_name, track_link, user_id):
    all_songs = load_data(all_songs_file , {})
    if track_id not in all_songs:
        all_songs[track_id] = {'track_name': track_name, 'track_link': track_link, 'recommended_by': user_id}
        save_data(all_songs, all_songs_file)
    else:
        return

def save_to_user_songs(track_id, track_name, track_link, user_id):
    user_songs = load_data(user_songs_file, [])  
    
    user_entry = next((entry for entry in user_songs if entry['user_id'] == user_id), None)
    
    if user_entry:
        user_entry['songs'].append({'track_id': track_id, 'track_name': track_name , 'track_link': track_link})
    else:
        user_songs.append({
            'user_id': user_id,
            'songs': [{'track_id': track_id, 'track_name': track_name, 'track_link': track_link}]
        })    
    save_data(user_songs, user_songs_file)

def save_recommendation(track_id, track_name, track_link, user_id):
    save_to_all_songs(track_id, track_name, track_link, user_id)
    save_to_user_songs(track_id, track_name, track_link, user_id)



#---------------- HELPER FUNCTIONS ----------------------------

def format_duration(ms: int) -> str:
    minutes, seconds = divmod(ms // 1000, 60)
    return f"{minutes}:{seconds:02d}"

def already_recommended(track_info):
    all_songs = load_data(all_songs_file, {})
    track_id = track_info['id']
    if track_id in all_songs:
        return all_songs[track_id]['recommended_by']
    return None    

def rearrange_queue(queue):
    user_to_songs = defaultdict(list)
    for song in queue:
        user_to_songs[song['recommended_by']].append(song)

    rearranged = []
    while any(user_to_songs.values()):
        for user_id in list(user_to_songs.keys()):
            if user_to_songs[user_id]:
                rearranged.append(user_to_songs[user_id].pop(0))
    return rearranged


#---------------------------- TASKS -------------------------------

async def send_daily_recommendations():
    try:
        recommendation_queue = load_queue()       #----
        if not recommendation_queue:
            return
        
        recommendation_channel = bot.get_channel(recommendation_channel_id)
        if not recommendation_channel:
            return
        guild = recommendation_channel.guild
        role = guild.get_role(1299382813384118323)

        recommendation = recommendation_queue.pop(0)
        
        embed = discord.Embed(
            title=recommendation['track_name']
        )
        
        user_id = recommendation['recommended_by']
        user = bot.get_user(user_id)
        user_mention = f"{user.mention} ({user.name})" if user else f"Unknown User ({user_id})"
        
        embed.add_field(name="Recommended By", value=user_mention, inline=False)
        embed.add_field(name="Artist(s)", value=recommendation['artist_names'], inline=False)
        embed.add_field(name="Album", value=recommendation['album_name'], inline=False)
        embed.add_field(name="Release Date", value=recommendation['album_release_date'], inline=False)
        embed.add_field(name="Duration", value=recommendation['track_duration'], inline=True)
        embed.add_field(name="Popularity", value=f"{recommendation['track_popularity']}/100", inline=True)
        embed.add_field(name="Explicit Content", value="Yes" if recommendation['is_explicit'] else "No", inline=True)
        embed.add_field(name="Listen on Spotify", value=f"[Click here]({recommendation['spotify_link']})", inline=False)

        if user:
            if user.avatar:
                embed.set_thumbnail(url=user.avatar.url)
            else:
                embed.set_thumbnail(url=user.default_avatar.url)

        if recommendation['cover_image_url']:
            embed.set_image(url=recommendation['cover_image_url'])

        await recommendation_channel.send(content=f"{role.mention}",embed=embed)
        await recommendation_channel.send(f'[Preview]({recommendation["spotify_link"]})')


        save_queue(recommendation_queue)
    except Exception as e:
        print(f"An error occurred while recommending {e}")

#------------------ COMMANDS ------------------------------------

class TrackSelectionView(View):
    def __init__(self, ctx, tracks):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.tracks = tracks
        self.index = 0
        self.user_confirmed = False
        self.selected_track = None

    def get_embed(self):
        track = self.tracks[self.index]
        track_name = track['name']
        artist_names = ", ".join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        spotify_link = track['external_urls']['spotify']
        cover_image_url = track['album']['images'][0]['url'] if track['album']['images'] else None

        embed = discord.Embed(title=f"Select Track ({self.index + 1}/{len(self.tracks)})")
        embed.add_field(name="Track", value=track_name, inline=False)
        embed.add_field(name="Artist(s)", value=artist_names, inline=False)
        embed.add_field(name="Album", value=album_name, inline=False)
        embed.add_field(name="Spotify Link", value=f"[Click here]({spotify_link})", inline=False)
        if cover_image_url:
            embed.set_thumbnail(url=cover_image_url)
        return embed
    
    def get_recommendation_data(self, ctx, track_info):
        track_name = track_info['name']
        artist_names = ", ".join([artist['name'] for artist in track_info['artists']])
        album_name = track_info['album']['name']
        album_release_date = track_info['album']['release_date']
        track_duration = format_duration(track_info['duration_ms'])
        track_popularity = track_info['popularity']
        cover_image_url = track_info['album']['images'][0]['url'] if track_info['album']['images'] else None
        spotify_link = track_info['external_urls']['spotify']
        is_explicit = track_info['explicit']
        recommendation_data = {
                'track_name': track_name,
                'artist_names': artist_names,
                'album_name': album_name,
                'album_release_date': album_release_date,
                'track_duration': track_duration,
                'track_popularity': track_popularity,
                'spotify_link': spotify_link,
                'is_explicit': is_explicit,
                'cover_image_url': cover_image_url,
                'recommended_by': ctx.author.id,
            }
        return recommendation_data
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction, button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("This is not for you.", ephemeral=True)
        if len(self.tracks) == 1:
            return await interaction.response.send_message("Single track selected", ephemeral=True)
        self.index = (self.index - 1) % len(self.tracks)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction, button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("This is not for you.", ephemeral=True)
        self.user_confirmed = False
        await interaction.response.defer()
        self.stop()
        
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction, button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("This is not for you.", ephemeral=True)
        user_id = already_recommended(self.tracks[self.index])
        if user_id:
            user = bot.get_user(user_id)
            await interaction.response.send_message(
                f"This track was already recommended by {user.mention}.",
                ephemeral=True
            )
            self.user_confirmed = False
            self.stop()
        else:
            self.user_confirmed = True
            self.selected_track = self.tracks[self.index]
            recommendation_queue = load_queue()  
            recommendation_queue.append(self.get_recommendation_data(self.ctx, self.selected_track))
            save_queue(recommendation_queue)
            await interaction.response.defer()
            self.stop()
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction, button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("This is not for you.", ephemeral=True)
        if len(self.tracks) == 1:
            return await interaction.response.send_message("Single track selected", ephemeral=True)
        self.index = (self.index + 1) % len(self.tracks)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)
    


    


class Recommend(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    # @commands.command(name="--rec")
    # async def add_rec(self, ctx: commands.Context, user: discord.Member, search_or_url: str):
    #     if ctx.author.id != 797359552874020954:
    #         return
    #     sent_message = await ctx.reply("Processing your recommendation . . .")

    #     match = spotify_url_regex.match(search_or_url)
    #     youtube_url_regex = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|.*v=)?(?P<id>[a-zA-Z0-9_-]+)')
    #     youtube_match = youtube_url_regex.match(search_or_url)
        
    #     try:
    #         if match:  # Spotify link detected
    #             await sent_message.edit(content="Spotify link detected")
    #             spotify_type = match.group(1)  
    #             spotify_id = match.group(2) 

    #             if spotify_type == "track":
    #                 track_info = sp.track(spotify_id)
    #             elif spotify_type == "playlist":
    #                 playlist_info = sp.playlist_tracks(spotify_id, limit=1)
    #                 track_info = playlist_info['items'][0]['track']
    #         elif youtube_match:  # YouTube link detected
    #             await sent_message.edit(content="YouTube prevents me from fetching metadata , please use text query or Spotify link")
    #             return
    #         else:  # General text search
    #             search_result = sp.search(q=search_or_url, type='track', limit=1)
    #             if search_result['tracks']['items']:
    #                 track_info = search_result['tracks']['items'][0]
    #             else:
    #                 await sent_message.edit(content="No results found for your query.")
    #                 return

    #         # Extract metadata
    #         track_id = track_info['id']
    #         track_name = track_info['name']
    #         artist_names = ", ".join([artist['name'] for artist in track_info['artists']])
    #         album_name = track_info['album']['name']
    #         album_release_date = track_info['album']['release_date']
    #         track_duration = format_duration(track_info['duration_ms'])
    #         track_popularity = track_info['popularity']
    #         cover_image_url = track_info['album']['images'][0]['url'] if track_info['album']['images'] else None
    #         spotify_link = track_info['external_urls']['spotify']
    #         is_explicit = track_info['explicit']

    #         recommendation_data = {
    #             'track_name': track_name,
    #             'artist_names': artist_names,
    #             'album_name': album_name,
    #             'album_release_date': album_release_date,
    #             'track_duration': track_duration,
    #             'track_popularity': track_popularity,
    #             'spotify_link': spotify_link,
    #             'is_explicit': is_explicit,
    #             'cover_image_url': cover_image_url,
    #             'recommended_by': user.id,
    #         }

    #         # Create and send the confirmation embed
    #         embed = discord.Embed(
    #             description="## Is this the correct track?"
    #         )
    #         embed.add_field(name="Track", value=track_name, inline=False)
    #         embed.add_field(name="Artist(s)", value=artist_names, inline=False)
    #         embed.add_field(name="Album", value=album_name, inline=False)
    #         embed.add_field(name="Spotify Link", value=f"[Click here]({spotify_link})", inline=False)

    #         if cover_image_url:
    #             embed.set_thumbnail(url=cover_image_url)

    #         view = ConfirmView(ctx, track_info, recommendation_data)
    #         await sent_message.edit(content=None, embed=embed, view=view)

    #         await view.wait()
    #         if not view.user_confirmed:
    #             await sent_message.edit(content=None, embed=discord.Embed(description="Recommendation cancelled."), view=None)
    #             return
    #         else:
    #             save_to_all_songs(track_id, track_name, spotify_link, user.id)
                
    #             await sent_message.edit(content=None, embed=discord.Embed(description="Song added to the queue!"), view=None)
    #     except Exception as e:
    #         await ctx.send(f"Error fetching details: {str(e)}")
    #         return
    
    

    
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    @commands.command(name="recommend" , description="Recommend songs that will sent as daily recommendations", aliases=["rec"])
    @commands.guild_only()
    # @discord.app_commands.describe(query="Search for a song")
    async def recommend(self, ctx: commands.Context,* , query: str):
        if ctx.guild.id != 1175730830371455016:
            return
        sent_message = await ctx.reply("Processing your recommendation...")

        match = spotify_url_regex.match(query)
        youtube_match = youtube_url_regex.match(query)

        try:
            if match:
                spotify_type = match.group(1)
                spotify_id = match.group(2)

                if spotify_type == "track":
                    track_info = sp.track(spotify_id)

                    track_id = track_info['id']
                    track_name = track_info['name']
                    artist_names = ", ".join([artist['name'] for artist in track_info['artists']])
                    album_name = track_info['album']['name']
                    spotify_link = track_info['external_urls']['spotify']
                    cover_image_url = track_info['album']['images'][0]['url'] if track_info['album']['images'] else None

                    embed = discord.Embed(title="Confirm Recommendation")
                    embed.add_field(name="Track", value=track_name, inline=False)
                    embed.add_field(name="Artist(s)", value=artist_names, inline=False)
                    embed.add_field(name="Album", value=album_name, inline=False)
                    embed.add_field(name="Spotify Link", value=f"[Click here]({spotify_link})", inline=False)
                    if cover_image_url:
                        embed.set_thumbnail(url=cover_image_url)

                    view = TrackSelectionView(ctx, [track_info])
                    await sent_message.edit(content=None, embed=embed, view=view)
                    await view.wait()

                    if not view.user_confirmed:
                        await sent_message.edit(content=None, embed=discord.Embed(description="Recommendation cancelled."), view=None)
                        return

                    # Save track
                    save_recommendation(track_id, track_name, spotify_link, ctx.author.id)
                    await sent_message.edit(content=None, embed=discord.Embed(description="Song added to the queue!"), view=None)

                elif spotify_type == "playlist":
                    await sent_message.edit(content=None, embed=discord.Embed(description=f"Cannot add playlists to the queue. Please try adding a single track."))

            elif youtube_match:
                await sent_message.edit(content="YouTube prevents me from fetching metadata, please use a text query or Spotify link.")
                return

            else:
                search_result = sp.search(q=query, type='track', limit=10)
                tracks = search_result['tracks']['items']
                if not tracks:
                    await sent_message.edit(content="No results found for your query.")
                    return

                view = TrackSelectionView(ctx, tracks)
                await sent_message.edit(content=None, embed=view.get_embed(), view=view)
                await view.wait()

                if not view.user_confirmed:
                    await sent_message.edit(content=None, embed=discord.Embed(description="Recommendation cancelled."), view=None)
                    return

                track_info = view.selected_track
                track_id = track_info['id']
                track_name = track_info['name']
                spotify_link = track_info['external_urls']['spotify']

                save_recommendation(track_id, track_name, spotify_link, ctx.author.id)
                await sent_message.edit(content=None, embed=discord.Embed(description="Song added to the queue!"), view=None)

        except Exception as e:
            await sent_message.edit(content=f"Error fetching details: {str(e)}")

    # @recommend.autocomplete('query')
    # async def autocomplete_songs(self, interaction: discord.Interaction, current: str):
    #     results = sp.search(q=current, type='track', limit=5)  # Spotify search in real-time
    #     choices = []
    #     for item in results['tracks']['items']:
    #         track_name = item['name']
    #         artist_names = ", ".join(artist['name'] for artist in item['artists'])
    #         choice_name = f"{track_name} - {artist_names}"
    #         choices.append(app_commands.Choice(name=choice_name[:100], value=item['id']))  # name is displayed, value is passed to command
    #     await interaction.response.send_autocomplete(choices)

    @commands.command(name="listallrec",description = "Shows all the songs recommended so far", aliases = ["allrec","all-recommendations"])   
    @commands.guild_only() 
    async def list_all_rec(self, ctx: commands.Context):
        if ctx.guild.id != my_guild_id:
            return
        all_songs = load_data(all_songs_file, {})
        all_songs_list = list(all_songs.items())
        total_songs = len(all_songs_list)

        songs_per_page = 50
        total_pages = (total_songs + songs_per_page - 1) // songs_per_page

        def create_embed(page):
            embed = discord.Embed(
                title=f"{total_songs} Recommended Songs",
                description=f"Page {page + 1}/{total_pages}\n"
            )
            start_index = page * songs_per_page
            end_index = min(start_index + songs_per_page, total_songs)

            for i, (track_id, track_info) in enumerate(all_songs_list[start_index:end_index], start=start_index + 1):
                track_name = track_info['track_name']
                track_link = track_info['track_link']
                embed.description += f"{i} . [{track_name}]({track_link})\n"
            return embed
        
        class SongsView(View):
            def __init__(self, message):
                super().__init__(timeout=300)
                self.page = 0
                self.message = message

            async def update_message(self, interaction):
                embed = create_embed(self.page)

                self.previous_page.disabled = self.page == 0
                self.next_page.disabled = self.page == total_pages - 1

                await interaction.response.edit_message(embed=embed, view = self)
            
            @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
            async def previous_page(self, interaction: discord.Interaction, button: Button):
                if self.page > 0:
                    self.page -= 1
                    await self.update_message(interaction)

            @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, disabled= True)
            async def next_page(self, interaction: discord.Interaction, button: Button):
                if self.page < total_pages - 1:
                    self.page += 1
                    await self.update_message(interaction)

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True
                
                if self.message:
                    await self.message.edit(embed=create_embed(self.page), view=self)
            
        initial_embed = create_embed(0)

        bot_message = await ctx.send(embed=initial_embed)

        view = SongsView(bot_message)

        view.next_page.disabled = total_pages == 1
        await bot_message.edit(view=view)

    @commands.command(name="listrec", desciption = "Shows song recommendations of an user", aliases=["recby","list-recommendations"])
    @commands.guild_only()
    async def show_songs(self, ctx: commands.Context, user: discord.User = None):
        if ctx.guild.id != my_guild_id:
            return
        if user is None:
            user = ctx.author
        user_songs = load_data(user_songs_file, [])
        
        user_entry = next((entry for entry in user_songs if entry['user_id'] == user.id), None)
        
        if not user_entry or not user_entry['songs']:
            await ctx.send(f"{user.mention} has not recommended any songs.")
            return

        user_recommendations = user_entry['songs']
        total_songs = len(user_recommendations)

        songs_per_page = 25
        total_pages = (total_songs + songs_per_page - 1) // songs_per_page  
        
        def create_embed(page):
            embed = discord.Embed(
                title=f"{total_songs} Songs recommended by {user.display_name}",
                description=f"Page {page + 1}/{total_pages}\n",
                color=discord.Color.blue()
            )
            start_index = page * songs_per_page
            end_index = min(start_index + songs_per_page, total_songs)

            for i in range(start_index, end_index):
                track = user_recommendations[i]
                track_name = track['track_name']
                track_link = track['track_link']
                embed.description += f"{i+1} . [{track_name}]({track_link})\n"
            return embed

        class SongsView(View):
            def __init__(self, message):
                super().__init__(timeout=300)
                self.page = 0
                self.message = message  
            
            async def update_message(self, interaction):
                embed = create_embed(self.page)

                self.previous_page.disabled = self.page == 0  
                self.next_page.disabled = self.page == total_pages - 1 

                await interaction.response.edit_message(embed=embed, view=self)

            @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
            async def previous_page(self, interaction: discord.Interaction, button: Button):
                if self.page > 0:
                    self.page -= 1
                    await self.update_message(interaction)

            @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
            async def next_page(self, interaction: discord.Interaction, button: Button):
                if self.page < total_pages - 1:
                    self.page += 1
                    await self.update_message(interaction)

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True

                if self.message:
                    await self.message.edit(embed=create_embed(self.page), view=self)

        initial_embed = create_embed(0)

        bot_message = await ctx.send(embed=initial_embed)

        view = SongsView(bot_message)

        view.next_page.disabled = total_pages == 1
        await bot_message.edit(view=view)

    @commands.command(name="upcoming-songs", description="Shows upcomings songs", aliases=["queue", "show-queue"]) 
    @commands.guild_only()   
    async def view_queue(self, ctx):
        if ctx.guild.id != my_guild_id:
            return
        song_queue = load_queue()     #-------------
        
        if not song_queue:
            await ctx.send("The song queue is currently empty.")
            return

        total_songs = len(song_queue)
        songs_per_page = 10

        def create_embed():
            embed = discord.Embed(
                title=f"{total_songs} song(s) in queue",
                description=f"### Upcoming Next\n",
                color=discord.Color.green()
            )
            upcoming_songs = song_queue[:songs_per_page]
            for i, song in enumerate(upcoming_songs, start=1):
                track_name = song['track_name']
                track_link = song['spotify_link']
                embed.description += f"{i}. [{track_name}]({track_link})\n"
            
            return embed
        embed = create_embed()
        await ctx.send(embed=embed)     


async def setup(bot: commands.Bot):
    await bot.add_cog(Recommend(bot))