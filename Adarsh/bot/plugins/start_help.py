# (c) adarsh-goel 
from Adarsh.bot import StreamBot
from Adarsh.vars import Var
import logging
logger = logging.getLogger(__name__)
from Adarsh.bot.plugins.stream import MY_PASS
from Adarsh.utils.human_readable import humanbytes
from Adarsh.utils.database import Database
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)
from pyrogram.types import ReplyKeyboardMarkup

 
  @xbot.on_message(filters.command('start') & filters.private)
async def _startfile(bot, update):
    if update.text == '/start':
        await update.reply_text(
            f"I'm File-Sharing!\nYou can share any telegram files and get the sharing link using this bot!\n\n/help for more details...",
            True, reply_markup=InlineKeyboardMarkup(START_BUTTONS))
        return

    if len(update.command) != 2:
        return
    code = update.command[1]
    if '-' in code:
        msg_id = code.split('-')[-1]
        # due to new type of file_unique_id, it can contain "-" sign like "agadyruaas-puuo"
        unique_id = '-'.join(code.split('-')[0:-1])

        if not msg_id.isdigit():
            return
        try:  # If message not belong to media group raise exception
            check_media_group = await bot.get_media_group(TRACK_CHANNEL, int(msg_id))
            check = check_media_group[0]  # Because func return`s list obj
        except Exception:
            check = await bot.get_messages(TRACK_CHANNEL, int(msg_id))

        if check.empty:
            await update.reply_text('Error: [Message does not exist]\n/help for more details...')
            return
        if check.video:
            unique_idx = check.video.file_unique_id
        elif check.photo:
            unique_idx = check.photo.file_unique_id
        elif check.audio:
            unique_idx = check.audio.file_unique_id
        elif check.document:
            unique_idx = check.document.file_unique_id
        elif check.sticker:
            unique_idx = check.sticker.file_unique_id
        elif check.animation:
            unique_idx = check.animation.file_unique_id
        elif check.voice:
            unique_idx = check.voice.file_unique_id
        elif check.video_note:
            unique_idx = check.video_note.file_unique_id
        if unique_id != unique_idx.lower():
            return
        try:  # If message not belong to media group raise exception
            await bot.copy_media_group(update.from_user.id, TRACK_CHANNEL, int(msg_id))
        except Exception:
            await check.copy(update.from_user.id)
    else:
        return


# Help msg
@xbot.on_message(filters.command('help') & filters.private)
async def _help(bot, update):
    await update.reply_text("Supported file types:\n\n- Video\n- Audio\n- Photo\n- Document\n- Sticker\n- GIF\n- Voice note\n- Video note\n\n If bot didn't respond, contact @xgorn", True)


async def __reply(update, copied):
    msg_id = copied.message_id
    if copied.video:
        unique_idx = copied.video.file_unique_id
    elif copied.photo:
        unique_idx = copied.photo.file_unique_id
    elif copied.audio:
        unique_idx = copied.audio.file_unique_id
    elif copied.document:
        unique_idx = copied.document.file_unique_id
    elif copied.sticker:
        unique_idx = copied.sticker.file_unique_id
    elif copied.animation:
        unique_idx = copied.animation.file_unique_id
    elif copied.voice:
        unique_idx = copied.voice.file_unique_id
    elif copied.video_note:
        unique_idx = copied.video_note.file_unique_id
    else:
        await copied.delete()
        return

    await update.reply_text(
        'Here is Your Sharing Link:',
        True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Sharing Link',
                                  url=f'https://t.me/{xbot_username}?start={unique_idx.lower()}-{str(msg_id)}')]
        ])
    )
    await asyncio.sleep(0.5)  # Wait do to avoid 5 sec flood ban 

# Store media_group
media_group_id = 0
@xbot.on_message(filters.media & filters.private & filters.media_group)
async def _main_grop(bot, update):
    global media_group_id
    if OWNER_ID == 'all':
        pass
    elif int(OWNER_ID) == update.from_user.id:
        pass
    else:
        return

    if int(media_group_id) != int(update.media_group_id):
        media_group_id = update.media_group_id
        copied = (await bot.copy_media_group(TRACK_CHANNEL, update.from_user.id, update.message_id))[0]
        await __reply(update, copied)

    else:
        # This handler catch EVERY message with [update.media_group_id] param
        # So we should ignore next >1_media_group_id messages
        return


# Store file
@xbot.on_message(filters.media & filters.private & ~filters.media_group)
async def _main(bot, update):
    if OWNER_ID == 'all':
        pass
    elif int(OWNER_ID) == update.from_user.id:
        pass
    else:
        return

    copied = await update.copy(TRACK_CHANNEL)
    await __reply(update, copied)


xbot.run()

@StreamBot.on_message(filters.command('start') & filters.private & ~filters.edited)
async def start(b, m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await b.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started !!"
        )
    usr_cmd = m.text.split("_")[-1]
    if usr_cmd == "/start":
        if Var.UPDATES_CHANNEL is not None:
            try:
                user = await b.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
                if user.status == "banned":
                    await b.send_message(
                        chat_id=m.chat.id,
                        text="**𝚈𝙾𝚄 𝙰𝚁𝙴 𝙱𝙰𝙽𝙽𝙴𝙳../**",
                        parse_mode="markdown",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                await b.send_message(
                    chat_id=m.chat.id,
                    text="**𝙹𝙾𝙸𝙽 𝙼𝚈 𝚄𝙿𝙳𝙰𝚃𝙴𝚉 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚃𝙾 𝚄𝚂𝙴 𝙼𝙴..**\n\n**𝙳𝚄𝙴 𝚃𝙾 𝙾𝚅𝙴𝚁𝙻𝙾𝙰𝙳 𝙾𝙽𝙻𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴𝚁𝚂 𝙲𝙰𝙽 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃..!**",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("Join Our Channel", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                            ]
                        ]
                    ),
                    parse_mode="markdown"
                )
                return
            except Exception:
                await b.send_message(
                    chat_id=m.chat.id,
                    text="**𝙰𝙳𝙳 𝙵𝙾𝚁𝙲𝙴 𝚂𝚄𝙱 𝚃𝙾 𝙰𝙽𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻**",
                    parse_mode="markdown",
                    disable_web_page_preview=True)
                return
        await m.reply_text(
            text="**👋 Hᴇʏ...!**\n\n<i>I'm Telegram Files Streaming Bot As Well Direct Links Generator</i>\n\n<i>Click On Help To Get More Information</i>\n\n<b><i><u>Warning 🚸</u></i></b>\n\n<b>🔞 Pron Contents Leads To Permanenet Ban You.</b>",
            reply_markup=InlineKeyboardMarkup(
                [[
                   InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
                   InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')
                ],        
                [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇꜱ", url='https://t.me/uploaddisk'),
                 InlineKeyboardButton("ʀᴇᴘᴏ", url='https://github.com/Selfie-bd/Filetolinkdcbot')]
                ]
            ),
            disable_web_page_preview=True
        )
    else:
        if Var.UPDATES_CHANNEL is not None:
            try:
                user = await b.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
                if user.status == "banned":
                    await b.send_message(
                        chat_id=m.chat.id,
                        text="__Sᴏʀʀʏ Sɪʀ, Yᴏᴜ ᴀʀᴇ Bᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴍᴇ.__\n\n**[Cᴏɴᴛᴀᴄᴛ Dᴇᴠᴇʟᴏᴘᴇʀ](https://t.me/uploaddisk_supportbot) Tʜᴇʏ Wɪʟʟ Hᴇʟᴘ Yᴏᴜ**",
                        parse_mode="markdown",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                await b.send_message(
                    chat_id=m.chat.id,
                    text="**𝙹𝙾𝙸𝙽 𝙼𝚈 𝚄𝙿𝙳𝙰𝚃𝙴𝚉 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚃𝙾 𝚄𝚂𝙴 𝙼𝙴..**\n\n**𝙳𝚄𝙴 𝚃𝙾 𝙾𝚅𝙴𝚁𝙻𝙾𝙰𝙳 𝙾𝙽𝙻𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴𝚁𝚂 𝙲𝙰𝙽 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃..!**",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("Join Our Channel", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                            ]                           
                        ]
                    ),
                    parse_mode="markdown"
                )
                return
            except Exception:
                await b.send_message(
                    chat_id=m.chat.id,
                    text="**𝙰𝙳𝙳 𝙵𝙾𝚁𝙲𝙴 𝚂𝚄𝙱 𝚃𝙾 𝙰𝙽𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻**",
                    parse_mode="markdown",
                    disable_web_page_preview=True)
                return

        get_msg = await b.get_messages(chat_id=Var.BIN_CHANNEL, message_ids=int(usr_cmd))

        file_size = None
        if get_msg.video:
            file_size = f"{humanbytes(get_msg.video.file_size)}"
        elif get_msg.document:
            file_size = f"{humanbytes(get_msg.document.file_size)}"
        elif get_msg.audio:
            file_size = f"{humanbytes(get_msg.audio.file_size)}"

        file_name = None
        if get_msg.video:
            file_name = f"{get_msg.video.file_name}"
        elif get_msg.document:
            file_name = f"{get_msg.document.file_name}"
        elif get_msg.audio:
            file_name = f"{get_msg.audio.file_name}"

        stream_link = "https://{}/{}".format(Var.FQDN, get_msg.message_id) if Var.ON_HEROKU or Var.NO_PORT else \
            "http://{}:{}/{}".format(Var.FQDN,
                                     Var.PORT,
                                     get_msg.message_id)

        msg_text = """
<u>**Successfully Generated Your Link !**</u>\n
<b>📂 File Name :</b> {}\n
<b>📦 File Size :</b> {}\n
<b>📥 Download :</b> {}\n
<b>🔗 File share :</b> {}\n
<b>🖥 Watch :</b> {}"""

        await m.reply_text(
            text=msg_text.format(file_name, file_size, stream_link),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚡ 𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳 𝙽𝙾𝚆 ⚡", url=stream_link)]])
        )


@StreamBot.on_message(filters.command('help') & filters.private & ~filters.edited)
async def help_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started !!"
        )
    if Var.UPDATES_CHANNEL is not None:
        try:
            user = await bot.get_chat_member(Var.UPDATES_CHANNEL, message.chat.id)
            if user.status == "banned":
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Sᴏʀʀʏ Sɪʀ, Yᴏᴜ ᴀʀᴇ Bᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴍᴇ.\n\n**[Cᴏɴᴛᴀᴄᴛ Dᴇᴠᴇʟᴏᴘᴇʀ](https://t.me/groupdcs) Tʜᴇʏ Wɪʟʟ Hᴇʟᴘ Yᴏᴜ**",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await bot.send_message(
                chat_id=message.chat.id,
                text="**𝙹𝙾𝙸𝙽 𝙼𝚈 𝚄𝙿𝙳𝙰𝚃𝙴𝚉 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚃𝙾 𝚄𝚂𝙴 𝙼𝙴..**\n\n**𝙳𝚄𝙴 𝚃𝙾 𝙾𝚅𝙴𝚁𝙻𝙾𝙰𝙳 𝙾𝙽𝙻𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴𝚁𝚂 𝙲𝙰𝙽 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃..!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Join Update Channel 🔰", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await bot.send_message(
                chat_id=message.chat.id,
                text="**𝙰𝙳𝙳 𝙵𝙾𝚁𝙲𝙴 𝚂𝚄𝙱 𝚃𝙾 𝙰𝙽𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻**",
                parse_mode="markdown",
                disable_web_page_preview=True)
            return
    await message.reply_text(
        text="**⪼ **How to Use Me ?**\n\n⪼ Send Me Any File Or Media From Telegram.\n⪼ I Will Provide External Direct Download Link !\n\n\n⪼Download Link With Fastest Speed ⚡️\n\n\nWarning ⚠️\n⪼ 🔞 Pron Contents Leads To Permanenet Ban You.\n\n⪼ Contact Developer Or Report Bugs : @groupdcs**",
  parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[
        InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
        InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')
        ],
        [
        InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='close'),
        ],        
        ]
        )
    )

@StreamBot.on_message(filters.command('about') & filters.private & ~filters.edited)
async def about_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started !!⚡"
        )
    if Var.UPDATES_CHANNEL is not None:
        try:
            user = await bot.get_chat_member(Var.UPDATES_CHANNEL, message.chat.id)
            if user.status == "banned":
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="__Sᴏʀʀʏ Sɪʀ, Yᴏᴜ ᴀʀᴇ Bᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴍᴇ.__\n\n**[Cᴏɴᴛᴀᴄᴛ Dᴇᴠᴇʟᴏᴘᴇʀ](https://t.me/groupdcs) Tʜᴇʏ Wɪʟʟ Hᴇʟᴘ Yᴏᴜ**",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await bot.send_message(
                chat_id=message.chat.id,
                text="**𝙹𝙾𝙸𝙽 𝙼𝚈 𝚄𝙿𝙳𝙰𝚃𝙴𝚉 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚃𝙾 𝚄𝚂𝙴 𝙼𝙴..**\n\n**𝙳𝚄𝙴 𝚃𝙾 𝙾𝚅𝙴𝚁𝙻𝙾𝙰𝙳 𝙾𝙽𝙻𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴𝚁𝚂 𝙲𝙰𝙽 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃..!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Join Updates Channel 🔰", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await bot.send_message(
                chat_id=message.chat.id,
                text="**🇮🇳**",
                parse_mode="markdown",
                disable_web_page_preview=True)
            return
    await message.reply_text(
        text="""<b>About Me and Owner 🌹</b>

<b>╭━━━━━━━〔File To Link〕</b>
┃
┣⪼<b>⚜ My Name : File To Link Bot</b>
┣⪼<b>⚜ Update : @UploadDisk</b>
┣⪼<b>🔸Version : 3.1.2</b>
┣⪼<b>🔹Last Updated : [ 29-Jan-23 ]</b>
┣⪼<b>✨Movie Channel: <a href='https://t.me/cinemadudes1'>Cinema Dudes</a></b>
┃
<b>╰━━━━━━━〔THANK YOU〕</b>""",
  parse_mode="html",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[
        InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
        InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help')
        ]]
        )
    )
