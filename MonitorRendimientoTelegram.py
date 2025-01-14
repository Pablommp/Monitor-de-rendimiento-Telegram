import os
import psutil
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests as req
import time

TELEGRAM_TOKEN = "7643811393:AAEQ-H-bnWNyVXAHExZozEOalRTyE9Zn5bk"

is_updating = False
message_id = None
chat_id = None
url = 'https://checkip.amazonaws.com'
last_message = ""


def comprobarCPU_RAM(uso):
    if uso > 80:
        return "🔴"
    elif uso > 50:
        return "🟠"
    else:
        return "🟢"


async def start_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_updating, message_id, chat_id, last_message, url

    try:
        request = req.get(url)
        ip = request.text.strip()
    except Exception as e:
        await update.message.reply_text(f"Error al obtener la IP: {e}")
        return

    if is_updating:
        await update.message.reply_text("El bot ya está actualizando el estado.")
        return

    is_updating = True
    chat_id = update.effective_chat.id

    sent_message = await context.bot.send_message(chat_id=chat_id, text="Recibiendo información...")
    message_id = sent_message.message_id

    start_time = time.time()  # Marca el tiempo inicial

    while is_updating:
        try:
            # Detener automáticamente después de 5 minutos
            if time.time() - start_time > 300:
                await update.message.reply_text("Se alcanzó el límite de 5 minutos. Deteniendo la actualización.")
                is_updating = False
                break

            cpu_percent = psutil.cpu_percent(interval=1)
            ram_percent = psutil.virtual_memory().percent
            ram_used = psutil.virtual_memory().used / (1024 ** 3)
            ram_total = psutil.virtual_memory().total / (1024 ** 3)

            new_message = f'''
💻 El sistema está activo 💻

Hora: {time.strftime('%H:%M:%S')}

IP: {ip}

CPU en uso: {cpu_percent}% {comprobarCPU_RAM(cpu_percent)}

RAM usada: {ram_percent}% {comprobarCPU_RAM(ram_percent)}

RAM usada (GB): {round(ram_used, 1)} de {round(ram_total, 1)} GB
            '''

            if new_message != last_message:
                await context.bot.edit_message_text(
                    chat_id=chat_id, message_id=message_id, text=new_message
                )
                last_message = new_message

            await asyncio.sleep(1)
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"Error: {e}")
            break

    is_updating = False


async def stop_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_updating

    if not is_updating:
        await update.message.reply_text("No hay ninguna actualización activa para detener.")
        return

    is_updating = False
    await update.message.reply_text("Se detuvo la actualización del estado.")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler("status", start_status)
    stop_handler = CommandHandler("stop", stop_status)

    application.add_handler(start_handler)
    application.add_handler(stop_handler)

    print("El bot está en ejecución...")
    application.run_polling()
