# GroupMe Bot Builder [Still in Development]

#### Easily build one or more bots into a single application. Supports regex handlers of incoming messages as well as cron jobs to perform functions on a regular cadence. Leverages decorators to cleanly add new functionality your bots.


```
pip install groupme-bot
```

### Multi Bot Example

```python
from groupme_bot import Router, Bot, Context, ImageAttachment, LocationAttachment


def mention_all(ctx: Context):
    ctx.bot.mention_all()


def attachments(ctx: Context):
    img_url = ctx.bot.image_url_to_groupme_image_url(image_url="https://images.indianexpress.com/2020/12/Doodle.jpg")
    image_attachment = ImageAttachment(image_url=img_url)
    location_attachment = LocationAttachment(name="A Location", lat=100.000, lng=46.000)
    ctx.bot.post_message("this is a message with attachments", [image_attachment, location_attachment])


def cron_task(ctx: Context):
    print(ctx.bot.bot_name)
    print("this is a scheduled function at the top of every hour")


bot1 = Bot('Fake bot 1',
           bot_id='fake-bot-id',
           groupme_api_token='fake-token',
           group_id='fake-group-id')

bot2 = Bot('Fake bot 2',
           bot_id='fake-bot-id',
           groupme_api_token='fake-token',
           group_id='fake-group-id')

# Available cron_task arguments: https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
bot1.add_cron_task(cron_task, minute=21, hour='*', timezone='America/Chicago')
bot1.add_callback_handler(r'^\\attachments', attachments)  # message starts with the string '\attachments'
bot1.add_callback_handler(r'^\\all', mention_all)  # message starts with the string '\all'
bot2.add_callback_handler(r'^\\all', mention_all)  # message starts with the string '\all'


if __name__ == '__main__':
    # create the bot router
    router = Router()

    # add the bots to the bot router
    router.add_bot(bot=bot1, callback_route="/bot1")
    router.add_bot(bot=bot2, callback_route="/bot2")

    # run both bots
    router.run(debug=True)

```
