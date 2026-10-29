import discord
from discord.ext import commands
# import giphy_client
# from giphy_client.rest import ApiException
from utils.emotes import get_emoji
# from models.actioncmds import GuildActionCmds
from models.userstats import UserStats
import random
import os
import json
import inflect
# import typing
# import aiohttp

ACTIONS_DIR = "cogs/fun"

def load_gifs(action: str) -> list[str]:
    path = os.path.join(ACTIONS_DIR, f"{action}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        data = json.load(f)
        return data

class ActionCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.allowed_actions = {"hug", "kiss", "pat", "bully", "tickle", "kick", "slap", "punch", "kill", "bite", "bonk"}
        # self.giphy_api_key = "6PTCW3cAg7oY3l8MwL4kHYUm8D7JzeF4"
        # self.tenor_api_key = "AIzaSyDhj636guwAsQwGP98H_QmY_SfSbWP-YbQ"
        for command in self.get_commands():
            command.cog_category = "Fun"
    
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    @commands.command(name="please", description="Perform actions on an user", aliases=["pls", "do"])
    @commands.guild_only()
    async def perform_action(self, ctx: commands.Context, action: str=None, member: discord.Member=None):
        async with ctx.typing():
            if not action and not member:
                return
            if ctx.message.reference and isinstance(ctx.message.reference.resolved, discord.Message):
                replied_to = ctx.message.reference.resolved
                if not member:
                    member = replied_to.author
            if action and not member:
                return await ctx.reply(embed=discord.Embed(description=f"{get_emoji('blobcatred')} Please mention a user to perform action on."), mention_author=False, delete_after=5)
            user_stats = UserStats.get_one(str(ctx.author.id), str(ctx.guild.id))
            if user_stats.balance < 30:
                return await ctx.reply(embed=discord.Embed(description=f"{get_emoji('blobcatred')} You don't have enough balance to perform actions."), mention_author=False, delete_after=5)
            if action.lower() not in self.allowed_actions:
                return await ctx.reply(embed=discord.Embed(description=f"**{get_emoji('blobcatred')} Please choose a valid action.**\nAvailable actions : ```{list(self.allowed_actions)}```"), delete_after=5)
            if member == ctx.author:
                wumpus = get_emoji("wumpusDance")
                return await ctx.send(embed=discord.Embed(description=f"It's not fun to perform actions on yourself, is it?\n# {wumpus}"))
            gifs = load_gifs(action)
            if not gifs:
                return await ctx.reply(embed=discord.Embed(description=f"No GIFs available for `{action}` yet."), mention_author=False)
            gif_url = random.choice(gifs)
            p = inflect.engine()
            action_word = p.plural(action.lower())
            user_stats.balance -= 30
            user_stats.save()
            embed = discord.Embed(
                color=discord.Color.random()
            )
            embed.set_author(
                name=f"{ctx.author.display_name} {action_word} {member.display_name}", 
                icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else ctx.author.default_avatar.url)
            embed.set_image(url=gif_url)
            await ctx.send(embed=embed) 

    # @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    # @commands.hybrid_command(name="ship", description="Ship members")           
            


#     @commands.hybrid_command(name="setup-actioncmds", description="Setup action commands for this guild", aliases=["setact", "setup-act"])
#     @commands.guild_only()
#     @discord.app_commands.describe(
#         rating="Choose the content rating for action commands (g, pg, pg-13, r)",
#         role="(Optional) Role required to use action commands"
#     )
#     async def setup_actioncmds(self, ctx: commands.Context, rating:typing.Literal["g", "pg", "pg-13", "r"], role: discord.Role=None):
#         if ctx.interaction: await ctx.defer()
#         async with ctx.typing():
#             if not ctx.author.guild_permissions.administrator:
#                 return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Administrator** permission to use this command."))
#             guild_id = str(ctx.guild.id)
#             role_id = str(role.id) if role else None
#             role_name = role.name if role else None
#             GuildActionCmds.save(guild_id, rating, role_id, role_name)
#             description = f"{get_emoji('checkmark')} Action commands have been setup as follows:\n- Rating `:` **{rating.upper()}**\n- Role Required `:` **{role.mention if role else 'None'}**"
#             embed = discord.Embed(title=f"{ctx.guild.name} Action Commands", description=description)
#             embed.set_footer(text="Use `content-ratings` command to learn more about content ratings.")
#             await ctx.send(embed=embed)
               
    # async def get_gif(self, search_term: str, limit: int, rating: str, server: int=1):
    #     if server == 1:
    #         rating_map = {
    #             "g": "low",
    #             "pg": "medium",
    #             "pg-13": "high",
    #             "r": "off"
    #         }
    #         client_key = "kaoru_bot"
    #         contentfilter = rating_map.get(rating, "medium")
    #         url = (
    #             f"https://tenor.googleapis.com/v2/search?q={search_term}"
    #             f"&key={self.tenor_api_key}&client_key={client_key}"
    #             f"&limit={limit}&contentfilter={contentfilter}"
    #         )
    #         try:
    #             async with aiohttp.ClientSession() as session:
    #                 # r = requests.get(url, timeout=5)/
    #                 async with session.get(url, timeout=5) as r:
    #                     if r.status == 200:
    #                         top_gifs = await r.json()
    #                         if "results" in top_gifs and top_gifs["results"]:
    #                             gifs = [gif["media_formats"]["gif"]["url"] for gif in top_gifs["results"] if "media_formats" in gif and "gif" in gif["media_formats"]]
    #                             return gifs if gifs else []
    #                             # if gifs:
    #                             #     return random.choice(gifs)
    #         except Exception as e:
    #             print(f"[ActionCommands] Tenor fetch error: {e}")

        # elif server == 2:
        #     api_instance = giphy_client.DefaultApi()
        #     try:
        #         response = api_instance.gifs_search_get(self.giphy_api_key, q=search_term, limit=limit, rating=rating)
        #         if not response.data:
        #             return None
        #         gif_list = list(response.data)     
        #         gif = random.choice(gif_list)
        #         return gif.images.original.url
        #     except ApiException as e:
        #         print(f"[ActionCommands] Tenor fetch error: {e}")

    # @commands.command(name="please", description="Perform any action with an user", aliases=["k"])
    # @commands.guild_only()
    # # @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.user)
    # async def action(self, ctx: commands.Context, action: str, member: discord.Member):
    #     async with ctx.typing():
    #         # guild_action = GuildActionCmds.get(str(ctx.guild.id))
    #         # role_id = guild_action.role_id
    #         # role = ctx.guild.get_role(int(role_id)) if role_id else None
    #         # if role and role not in ctx.author.roles and not ctx.author.guild_permissions.administrator:
    #         #     return await ctx.send(embed=discord.Embed(description=f"{get_emoji('blobcatred')} You need **{role.mention}** role to perform actions."))
    #         # user_stats = UserStats.get_one(str(ctx.author.id), str(ctx.guild.id))
    #         # if user_stats.balance < 30:
    #         #     return await ctx.reply(embed=discord.Embed(description=f"{get_emoji('blobcatred')} You don't have enough balance to perform actions."), mention_author=False, delete_after=5)
    #         if member == ctx.author:
    #             wumpus = get_emoji("wumpusDance")
    #             return await ctx.send(embed=discord.Embed(description=f"It's not fun to perform actions on yourself, is it?\n# {wumpus}"))

    #         # rating = guild_action.rating if guild_action.rating else None
    #         # common_actions = ["kick", "kiss", "punch", "hug", "pat"]
    #         # prefixs = ["anime", "cat", ""] if action.lower() in common_actions else ["anime", ""]
    #         # prefix = action.split('-', 1)[0] if '-' in action else random.choice(prefixs)
    #         # content = action.split('-', 1)[1] if '-' in action else action 
    #         search_term = f"anime {action}"
    #         limit = 60
            
    #         gif_to_send = await self.get_gif(search_term, limit, rating=None, server=1)
    #         # if not gif_to_send:
    #         #     gif_to_send = await self.get_gif(search_term, limit, rating, server=unselected_server)
    #         if not gif_to_send:
    #             return await ctx.send(embed=discord.Embed(description=f"{get_emoji('blobcatred')} Uh oh, you misserably failed to **{action}** {member.mention}.\n Better luck next time!"))
            
    #         # user_stats.balance -= 1
    #         # user_stats.save()
    #         p = inflect.engine()
    #         action_word = p.plural(action)
    #         for gif in gif_to_send:
    #             embed = discord.Embed(description=f"```{gif}```")
    #             embed.set_author(
    #                 name=f"{ctx.author.display_name} {action_word} {member.display_name}", 
    #                 icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else ctx.author.default_avatar.url)
    #             embed.set_image(url=gif)
    #             embed.set_footer(text=f"Run `actioncmds` to learn more about action commands")
    #             await ctx.send(embed=embed)
    
#     @commands.command(name="actioncmds", description="Learn more about action commands", aliases=["acmds"])
#     @commands.guild_only()
#     async def actioncmds(self, ctx: commands.Context):
#         async with ctx.typing():
#             guild_action = GuildActionCmds.get(str(ctx.guild.id))
#             embed = discord.Embed(title="Action Commands Guide",
#                         description=f"""
# - **Use case 1** `:` Simply type `pls <action> <@user>` - This chooses a random prefix (cat, anime, etc) for the given.
# - **Use case 2** `:` Type `pls <prefix>-<action> <@user>` - This allows you to specify a prefix for the action.""")
#             embed.add_field(name=f"{ctx.guild.name} Settings",
#                             value=f"""
# - **Content Rating** `:` **{guild_action.rating.upper() if guild_action.rating else 'Not Set'}**
# - **Role Required** `:` **{ctx.guild.get_role(int(guild_action.role_id)).mention if guild_action.role_id else 'None'}**""", inline=False)
#             embed.add_field(name="Balance Requirement", 
#                             value=f"30 {get_emoji('ecoin')} will be deducted from your balance for each action.\nYou currenty have **{UserStats.get_one(str(ctx.author.id), str(ctx.guild.id)).balance}** {get_emoji('ecoin')}.", inline=False)
#             embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
#             await ctx.send(embed=embed)
       
    
#     @commands.command(name="content-ratings", description="Learn about content ratings for action commands", aliases=["ctr"])
#     @commands.guild_only()
#     async def content_ratings(self, ctx: commands.Context):
#         async with ctx.typing():
#             crl_description = f"""
# ## Content Rating Levels
# **{get_emoji('blobcatgreen')} __Level-1 (G)__** `:` **Contains images that are broadly accepted as appropriate and commonly witnessed by people in a public environment.**
# - No profanity
# - No sexual content - real or animated (no innuendo or partial nudity, nothing provocative)
# - No violence or threatening imagery
# - No weapons (finger, water, and Nerf guns are exceptions)
# - No substances/drugs

# **{get_emoji('blobcatblue')} __Level-2 (PG)__** `:` **Contains images that are commonly witnessed in a public environment, but not as broadly accepted as appropriate.**
# - Mild profanity (ex: butt, hell, damn, suck, etc.)
# - Mild bathroom humor
# - Mild sexual content (ex: kissing on the lips, fully clothed provocative body movements.)
# - Mild violence (yelling angrily, smashing inanimate objects, fails, facetious references to acts of violence, etc.)
# - Images that feature real guns in holsters and people aiming or shooting non realistic looking guns from pop culture
# - Images with medieval weapons with no blood and mild duels without injury
# - Mildly abnormal or frightening activities, movements, or gestures (ex: spooky images from horror movies without gore, horror makeup, etc.)
# - Images of tobacco and alcohol, their brand names, and mild usage (ex: sipping, cheers, holding cigarettes, etc.)

# **{get_emoji('blobcatorange')} __Level-3 (PG-13)__** `:` **Contains images that are typically not seen unless sought out, but still commonly witnessed.**
# - Moderate profanity and implied abbreviations (ex: human anatomy, names of drugs, wtf, etc.)
# - Use of middle finger as a rude gesture
# - Sexual content and themes, including sexual innuendo with no nudity (ex. making out, sexually suggestive movements, references to sex acts)
# - Exploitation of the human body while partially covered
# - Images featuring non-gushing blood in a violent context
# - Moderately violent or threatening behaviour or gestures (ex: pointing a knife, excerpts from horror movies, knockouts, injury)
# - Realistic guns (ex: guns being held, pointed, shot, etc.)
# - Heavy use of alcohol (ex: chugging, keg stands, beer bogs, etc.)
# - References to marijuana, illegal drug use, and fictional images of use
# - Challenging religion or religious figures

# **{get_emoji('blobcatred')} __Level-4 (R)__** `:` **Contains images that are typically not seen unless sought out and could be considered alarming if witnessed.**
# - Severe profanity
# - Nonpornographic images with strong sexual themes and innuendo, very revealing clothing, main focus on bodies, and otherwise arousing images with partial nudity.
# - Crudely drawn or humorous cartoons or CGI that depicts genitalia
# - Imagery and content from movies, TV, and video games that is highly disturbing, alarming, distressing, or dark, even if there is no gore
# - Any simulated violence with gore
# - Heavy use of illegal drugs in a fictional settings
# - Very crude and vulgar humor"""
#             embed = discord.Embed(description=crl_description)
#             await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ActionCommands(bot)) 



