# DCinside Discord Bot
Discord chat bot that perpetually monitors selected dcinside forums and sends details of new posts to a discord channel as a message.
Please note that as this program monitors the Korean forums, it only supports Korean commands. 

## Purpose of this program
This bot program was built in order to monitor multiple forums easily on one discord channel.

## How to use
This bot program requires a user to create a discord bot and implement on a discord channel before running the code.
Then, input the bot token on to the script to run the bot.<br>
After running a bot program, a user can add or remove the dcinside forums to monitor, see a list of added forums and toggle on/off the monitoring.<br>
The following commands can be used on the discord channel:<br>
- To add a new forum to the system, type !등록 <갤러리이름> <갤러리영문링크> <갤러리마이너변수>.
<br>  ^ <i>manual addtion of forum to the bot system in case the bot doesn't recognise</i>
- To add or delete a forum to monitor, type !추가 <갤러리이름> or !삭제 <갤러리이름>.
- To see a list of monitoring forums, type !리스트.
- To toggle on/off motinoring, type !시작 or !중지.
- To view bot's current status, type !상태.

## How it works
This program is made of three main parts; web crawler, database and Discord API.

#### Web crawler
By using threading module, web crawling is done on selected forums constantly as a separate thread.<br>
The web crawled post data is then preprocessed and saved into the database.

#### Database
The sqlite3 module is implemented as a database management system, where the preprocessed forum data is saved locally.<br>
The data saved here is used for comparison against newly web crawled data to determine newly uploaded posts.

#### Discord API
The discord.py module is used as a Discord API wrapper. Event functions are built using this module to respond to a user's commands on a discord channel. <br>
The commands allow users to add or remove forums to the web crawler and send new post details to the channel.

## How it looks on Discord channel
As shown in the screenshot below, the bot constantly sends a message containing post information whenever there is a new post on the selected forums. <br>
The message includes forum name, post title, writer and post time. <br>
![alt text](https://github.com/anonydev003/DC_Discord/raw/master/sample.jpg) <br>
#### Updated message output to be embed message <br>
![alt text](https://github.com/anonydev003/DC_Discord/raw/master/dcbotsample.png)
