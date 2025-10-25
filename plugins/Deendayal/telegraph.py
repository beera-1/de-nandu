import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

CATBOX_API = "https://catbox.moe/user/api.php"

@Client.on_message(filters.command(["img", "cup", "catbox"], prefixes="/") & filters.reply)
async def c_upload(client, message: Message):
    reply = message.reply_to_message
    user_mention = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"

    if not reply.media:
        return await message.reply_text("Reply to an image, video, or audio file (max 200MB) to upload to Catbox.")

    if reply.document and reply.document.file_size > 200 * 1024 * 1024:
        return await message.reply_text("File size limit is 200MB for Catbox.")

    msg = await message.reply_text("Uploading your masterpiece... 🎨✨")

    try:
        downloaded_media = await reply.download()

        if not downloaded_media:
            return await msg.edit_text("Oops! Something went wrong during the download. Try again.")

        with open(downloaded_media, "rb") as f:
            response = requests.post(CATBOX_API, data={"reqtype": "fileupload"}, files={"fileToUpload": f})

        if response.status_code == 200:
            file_url = response.text.strip()

            # Create share button
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Share This", url=file_url)]]
            )

            # Unique caption with user mention
            caption_text = (
                f"🎉 **Great news, {user_mention}!** Your file is now floating in the cloud! ☁️🚀\n\n"
                f"🔗 **Access it here:** [Click to View]({file_url})\n"
                f"💡 **Tip:** Share it before it gets lost in the digital universe!"
            )

            # Send instant preview for images & videos
            if reply.photo:
                await message.reply_photo(photo=file_url, caption=caption_text, reply_markup=buttons)
            elif reply.video:
                await message.reply_video(video=file_url, caption=caption_text, reply_markup=buttons)
            else:
                await msg.edit_text(caption_text, reply_markup=buttons)

        else:
            await msg.edit_text("Upload failed. Maybe try again? 🤔")

        os.remove(downloaded_media)

    except Exception as e:
        await msg.edit_text(f"Uh-oh! Something went wrong: `{str(e)}`")
