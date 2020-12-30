# GroupMe Bot Builder

#### Easily build one or more bots into a single application. Supports regex handlers of incoming messages as well as cron jobs to perform functions on a regular cadence.


```
pip install groupme-bot
```

## Usage

- An Application object is created to house one or many Bot objects and route incoming traffic to the correct Bot. Each Bot is registered at it's own url path
to allow for Bots to easily setup callbacks in the GroupMe Developer site.
- A separate Bot object is defined for each bot and can include the following handlers:
    - Regexp Handlers: If a message is sent to the group that matches the given regex, the associated handler function will be called
    - Cron Jobs: Handler functions that will be run on a set cron cadence
- Handler functions all take one argument (context) which is of type Context. The Context contains both a reference to the Bot object being called and the Callback object containing the payload from GroupMe.
    - The passing of the Bot object in the Context allows for handler functions to be universal and shared by multiple Bots.
    
### Running Your App

Start your app with [Uvicorn](http://www.uvicorn.org/deployment/). For more deployment details, see http://www.uvicorn.org/deployment/.

Example running an `app` object in `main.py`.

**Must use `--workers=1` to prevents scheduled jobs from running multiple times. Working on a fix for this.**

```
uvicorn main:app --workers=1
```

### Multi Bot Example

```python
# main.py

import re 

from groupme_bot import Application, Bot, Context, ImageAttachment, LocationAttachment


# create the bot Application
app = Application()


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

# add cron job
#  - available cron_task arguments: https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
bot1.add_cron_job(cron_task, minute=0, hour='*', timezone='America/Chicago')

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
```
