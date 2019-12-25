# dcinside_discord_bot
Discord bot that perpetually monitors selected dcinside forums and sends details of new posts to a discord channel as a message.
Please note that as this program monitors the Korean forums, it only supports Korean commands. 

## Purpose of this program
This bot program was built in order to monitor multiple forums easily on one discord channel.

## How to use
This bot program requires a use to create a discord bot and implement on a discord channel before running the code.
Then, input the bot token on to the script to run the bot.<br>
After running a bot program, a user can add or remove the dcinside forums to monitor, see a list of added forums and toggle on/off the monitoring.<br>
The following commands can be used on the discord channel:<br>
- To add or delete a forum, type !추가 <갤러리이름> or !삭제 <갤러리이름>.
- To see a list of added forums, type !리스트.
- To toggle on/off the function, type !시작 or !중지.

## How this works
This program can be separated into three parts; web crawler, database and Discord API.

#### Web crawler
By using threading module, web crawling is done on selected forums constantly.<br>
The web crawled post data is then preprocessed and saved into the database.

#### Database
The sqlite3 module is implemented as a database management system, where the preprocessed forum data is saved locally.<br>
The data saved here is used for comparison against newly web crawled data to determine newly uploaded posts.

#### Discord API
The discord.py module is used as a Discord API wrapper. Event functions are built using this module to respond to a user's commands on a discord channel. <br>
The commands allow users to add or remove forums to the web crawler and send new post details to the channel.


![alt text](https://github.com/anonydev003/DC_Discord/raw/master/sample.jpg)
