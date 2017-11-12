from discord.ext import commands
from random import choice, shuffle
import aiohttp
import functools
import asyncio

try:
    from imgurpython import ImgurClient
except:
    ImgurClient = False

CLIENT_ID = "1fd3ef04daf8cab"
CLIENT_SECRET = "f963e574e8e3c17993c933af4f0522e1dc01e230"
GIPHY_API_KEY = "dc6zaTOxFJmzC"


class Image:
    """Commande de gestion d'images."""

    def __init__(self, bot):
        self.bot = bot
        self.imgur = ImgurClient(CLIENT_ID, CLIENT_SECRET)

    @commands.group(name="imgur", no_pm=True, pass_context=True)
    async def _imgur(self, ctx):
        """Récupère des images d'Imgur"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_imgur.command(pass_context=True, name="random")
    async def imgur_random(self, ctx, *, term: str=None):
        """Renvoie une image aléatoire d'Imgur

        Un champ de recherche peut être précisé"""
        if term is None:
            task = functools.partial(self.imgur.gallery_random, page=0)
        else:
            task = functools.partial(self.imgur.gallery_search, term,
                                     advanced=None, sort='time',
                                     window='all', page=0)
        task = self.bot.loop.run_in_executor(None, task)

        try:
            results = await asyncio.wait_for(task, timeout=10)
        except asyncio.TimeoutError:
            await self.bot.say("**Erreur** | Timeout atteint ; Les serveurs d'Imgur peuvent ne pas être disponible")
        else:
            if results:
                item = choice(results)
                link = item.gifv if hasattr(item, "gifv") else item.link
                await self.bot.say(link)
            else:
                await self.bot.say("**Aucun résultat**")

    @_imgur.command(pass_context=True, name="search")
    async def imgur_search(self, ctx, *, term: str):
        """Renvoie 3 images en rapport avec votre recherche"""
        task = functools.partial(self.imgur.gallery_search, term,
                                 advanced=None, sort='time',
                                 window='all', page=0)
        task = self.bot.loop.run_in_executor(None, task)

        try:
            results = await asyncio.wait_for(task, timeout=10)
        except asyncio.TimeoutError:
            await self.bot.say("**Erreur** | Timeout atteint ; Les serveurs d'Imgur peuvent ne pas être disponible")
        else:
            if results:
                shuffle(results)
                msg = "**Recherche** | Patientez...\n"
                for r in results[:3]:
                    msg += r.gifv if hasattr(r, "gifv") else r.link
                    msg += "\n"
                await self.bot.say(msg)
            else:
                await self.bot.say("**Aucun résulat**")

    @_imgur.command(pass_context=True, name="subreddit")
    async def imgur_subreddit(self, ctx, subreddit: str, sort_type: str="top", window: str="day"):
        """Renvoie une image en rapport avec le subreddit lié

        Termes de tri: new, top
        Fenêtres de temps: day, week, month, year, all"""
        sort_type = sort_type.lower()

        if sort_type not in ("new", "top"):
            await self.bot.say("**Erreur** | Seuls *new* et *top* fonctionnent pour trier les résultats.")
            return
        elif window not in ("day", "week", "month", "year", "all"):
            await self.bot.send_cmd_help(ctx)
            return

        if sort_type == "new":
            sort = "time"
        elif sort_type == "top":
            sort = "top"

        links = []

        task = functools.partial(self.imgur.subreddit_gallery, subreddit,
                                 sort=sort, window=window, page=0)
        task = self.bot.loop.run_in_executor(None, task)
        try:
            items = await asyncio.wait_for(task, timeout=10)
        except asyncio.TimeoutError:
            await self.bot.say("**Erreur** | Timeout atteint ; Les serveurs d'Imgur peuvent ne pas être disponible")
            return

        for item in items[:3]:
            link = item.gifv if hasattr(item, "gifv") else item.link
            links.append("{}\n{}".format(item.title, link))

        if links:
            await self.bot.say("\n".join(links))
        else:
            await self.bot.say("**Aucun résultat**")

def setup(bot):
    if ImgurClient is False:
        raise RuntimeError("You need the imgurpython module to use this.\n"
                           "pip3 install imgurpython")

    bot.add_cog(Image(bot))
