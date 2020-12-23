# GroupMe Bot Builder

#### Easily build one or more bots into a single application. Supports regex handlers of incoming messages as well as cron jobs to perform functions on a regular cadence.


```
pip install groupme-bot
```

### Multi Bot Example

```python
import re 

from groupme_bot import Router, Bot, Context, ImageAttachment, LocationAttachment

# define handler functions
def cron_task(ctx: Context):
    print(ctx.bot.bot_name)
    print("this is a scheduled function at the top of every hour")

def mention_all(ctx: Context):
    ctx.bot.mention_all()
    
def attachments(ctx: Context):
    img_url = ctx.bot.image_url_to_groupme_image_url(image_url="https://images.indianexpress.com/2020/12/Doodle.jpg")
    image_attachment = ImageAttachment(image_url=img_url)
    location_attachment = LocationAttachment(name="A Location", lat=100.000, lng=46.000)
    ctx.bot.post_message("this is a message with attachments", [image_attachment, location_attachment])

def gif_search(ctx: Context):
    sr = re.search(r'^\\gif([a-zA-Z0-9 -_]+)', ctx.callback.text)
    if sr:
        query_string = sr.group(1).strip()
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

# add cron task
#  - available cron_task arguments: https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
bot1.add_cron_task(cron_task, minute=0, hour='*', timezone='America/Chicago')

# add callback handlers
bot1.add_callback_handler(r'^\\attachments', attachments)  # message starts with the string '\attachments'
bot1.add_callback_handler(r'^\\all', mention_all)  # message starts with the string '\all'
bot2.add_callback_handler(r'^\\all', mention_all)  # message starts with the string '\all'
bot2.add_callback_handler(r'^\\gif', gif_search)  # message starts with the string '\gif'


if __name__ == '__main__':
    # create the bot router
    router = Router()

    # add the bots to the bot router
    router.add_bot(bot=bot1, callback_route="/bot1")
    router.add_bot(bot=bot2, callback_route="/bot2")

    # run both bots
    router.run(debug=True)

```
