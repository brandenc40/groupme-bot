import re

from groupme_bot import Application, Bot, Context, ImageAttachment, LocationAttachment

# create the bot Application
app = Application()


# define handler functions
async def cron_task(ctx: Context):
    print('Cron triggered for ' + str(ctx.bot))


def mention_all(ctx: Context):
    print('mention_all for ' + str(ctx.bot))
    ctx.bot.mention_all()


def attachments(ctx: Context):
    print('attachments for ' + str(ctx.bot))
    img_url = ctx.bot.image_url_to_groupme_image_url(image_url="https://images.indianexpress.com/2020/12/Doodle.jpg")
    image_attachment = ImageAttachment(image_url=img_url)
    location_attachment = LocationAttachment(name="A Location", lat=100.000, lng=46.000)
    ctx.bot.post_message("this is a message with attachments", [image_attachment, location_attachment])


def gif_search(ctx: Context):
    print('gif_search for ' + str(ctx.bot))
    sr = re.search(r'^\\gif([a-zA-Z0-9 -_]+)', ctx.callback.text)
    if sr:
        # query_string = sr.group(1).strip()
        # gif_result = search_for_gif(query_string)
        # ctx.bot.post_message(gif_result)
        print("implement something like this ^")


# build the bot objects
bot1 = Bot('Fake bot 1',
           bot_id='fake-bot-id',
           groupme_api_token='fake-token',
           group_id='fake-group-id')

bot2 = Bot('Fake bot 2',
           bot_id='fake-bot-id',
           groupme_api_token='fake-token',
           group_id='fake-group-id')

# add cron job
#  - available cron_task arguments: https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
bot1.add_cron_job(cron_task, minute='*', hour='*', timezone='America/Chicago')

# add callback handlers
bot1.add_callback_handler(r'^\\attachments', attachments)  # message starts with the string '\attachments'
bot1.add_callback_handler(r'^\\all', mention_all)  # message starts with the string '\all'
bot2.add_callback_handler(r'^\\all', mention_all)  # message starts with the string '\all'
bot2.add_callback_handler(r'^\\gif', gif_search)  # message starts with the string '\gif'

# add the bots to the bot router
app.add_bot(bot=bot1, callback_path="/bot1")
app.add_bot(bot=bot2, callback_path="/bot2")

# to run:
# `uvicorn main:app --workers=1`
