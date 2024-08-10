from helper.utils import progress_for_pyrogram, convert, random_file_name
from pyrogram import Client, filters
from pyrogram.types import (  InlineKeyboardButton, InlineKeyboardMarkup,ForceReply)
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.database import db
import os 
import humanize
from PIL import Image
import time

@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot,update):
	try:
           await update.message.delete()
	except:
           return

@Client.on_callback_query(filters.regex('rename'))
async def rename(bot,update):
	user_id = update.message.chat.id
	date = update.message.date
	await update.message.delete()
	await update.message.reply_text("**__ᴩʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ɴᴇᴡ ꜰɪʟᴇɴᴀᴍᴇ...__**",	
	reply_to_message_id=update.message.reply_to_message.id,  
	reply_markup=ForceReply(True))
	
@Client.on_callback_query(filters.regex("upload"))
async def doc(bot,update):
     type = update.data.split("_")[1]
     new_name = update.message.text
     new_filename = new_name.split(":-")[1]
     file_path = f"downloads/{new_filename}"
     file = update.message.reply_to_message
     media = getattr(file, file.media.value)
     ms = await update.message.edit("`ᴛʀʏ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ....`")    
    try:
        custom_file_name = random_file_name(5)
        down_file_name = "downloads" + "/" + str(update.from_user.id) + f"{custom_file_name}" + f"{media.file_name}"
        path = await bot.download_media(message=file, file_name=down_file_name, progress=progress_for_pyrogram, progress_args=("ᴅᴏᴡɴʟᴏᴀᴅ sᴛᴀʀᴛᴇᴅ....", ms, time.time()))                    
    except Exception as e:
        return await ms.edit(e)

    splitpath = path.split("/downloads/")
    dow_file_name = splitpath[1]
    old_file_name = f"downloads/{dow_file_name}"
    os.rename(old_file_name, file_path)
     	     
    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()
    except:
        pass
	    
    ph_path = None
    media = getattr(file, file.media.value)
    c_caption = await db.get_caption(update.message.chat.id)
    c_thumb = await db.get_thumbnail(update.message.chat.id)

    if c_caption:
         try:
             caption = c_caption.format(filename=new_filename, filesize=humanize.naturalsize(media.file_size), duration=convert(duration))
         except Exception as e:
             await ms.edit(text=f"Your caption Error unexpected keyword ●> ({e})")
             return 
     else:
         caption = f"**{new_filename}**"
     if (media.thumbs or c_thumb):
         if c_thumb:
            ph_path = await bot.download_media(c_thumb) 
         else:
            ph_path = await bot.download_media(media.thumbs[0].file_id)
         Image.open(ph_path).convert("RGB").save(ph_path)
         img = Image.open(ph_path)
         img.resize((320, 320))
         img.save(ph_path, "JPEG")
     await ms.edit("**__ᴛʀyɪɴɢ ᴛᴏ ᴜᴩʟᴏᴀᴅɪɴɢ....__**")
     c_time = time.time() 
     try:
        if type == "document":
           await bot.send_document(
		    update.message.chat.id,
                    document=file_path,
                    thumb=ph_path, 
                    caption=caption, 
                    progress=progress_for_pyrogram,
                    progress_args=( "**__ᴛʀyɪɴɢ ᴛᴏ ᴜᴩʟᴏᴀᴅɪɴɢ....__**",  ms, c_time   ))
        elif type == "video": 
            await bot.send_video(
		    update.message.chat.id,
		    video=file_path,
		    caption=caption,
		    thumb=ph_path,
		    duration=duration,
		    progress=progress_for_pyrogram,
		    progress_args=( "**__ᴛʀyɪɴɢ ᴛᴏ ᴜᴩʟᴏᴀᴅɪɴɢ....__**",  ms, c_time))
        elif type == "audio": 
            await bot.send_audio(
		    update.message.chat.id,
		    audio=file_path,
		    caption=caption,
		    thumb=ph_path,
		    duration=duration,
		    progress=progress_for_pyrogram,
		    progress_args=( "**__ᴛʀyɪɴɢ ᴛᴏ ᴜᴩʟᴏᴀᴅɪɴɢ....__**",  ms, c_time   )) 
     except Exception as e: 
         await ms.edit(f" Erro {e}") 
         os.remove(file_path)
         if ph_path:
           os.remove(ph_path)
         return 
     await ms.delete() 
     os.remove(file_path) 
     if ph_path:
        os.remove(ph_path) 
