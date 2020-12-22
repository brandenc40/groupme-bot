# GroupMe Bot Builder [Still in Development]

#### Easily build one or more bots into a single application. Supports regex handlers of incoming messages as well as cron jobs to perform functions on a regular cadence. Leverages decorators to cleanly add new functionality your bots.

- Availble cron_task arguments: https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html

```
pip install groupme-bot
```

### Multi Bot Example

```python

from groupme_bot import Bot, Router, Callback, ImageAttachment, LocationAttachment


# define bot 1 and add a handler
bot1 = Bot('Fake bot 1', bot_id='bot1-bot-id', api_token='bot1-groupme-api-token', group_id='bot1-group-id')

@bot1.callback_handler(r'\\attachments.+')  # message starts with the string '\attachments'
def bot1_help(_: Callback):
    img_url = bot1.image_url_to_groupme_image_url(image_url="https://images.indianexpress.com/2020/12/Doodle.jpg")
    image_attachment = ImageAttachment(image_url=img_url)
    location_attachment = LocationAttachment(name="A Location", lat=100.000, lng=46.000)
    bot1.post_message("this is a message with attachments", [image_attachment, location_attachment])



# define bot 2 and add a handler and a cron task
bot2 = Bot('Fake bot 2', bot_id='bot2-bot-id', api_token='bot2-groupme-api-token', group_id='bot2-group-id')

@bot2.callback_handler(r'\\all.+')  # message starts with the string '\all'
def bot2_mention_all(_: Callback):
    bot2.mention_all()

@bot2.cron_task(minute=0, hour='*', timezone='America/Chicago')
def test_cron_task():
    print("this is a scheduled function at the top of every hour")


# create the bot router
router = Router()

# add the bots to the bot router
router.add_bot(bot=bot1, callback_route="/bot1")
router.add_bot(bot=bot2, callback_route="/bot2")

if __name__ == '__main__':
    # run both bots
    router.run(debug=True)
    
```
