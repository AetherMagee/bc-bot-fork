import asyncio
import datetime
import random

from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from handlers.pidor import db
from handlers.pidor.rus_util import format_timedelta_ru

BEGINNING_STRINGS = [
    "Эй, зачем разбудили...",
    "### RUNNING 'TYPIDOR.SH'...",
    "Инициирую поиск пидора дня...",
    "Зачем вы меня разбудили...",
    "Woop-woop! That's the sound of da pidor-police!",
    "Осторожно! <b>Пидор дня</b> активирован!",
    "Что тут у нас?"
]
PROCESS_STRINGS = [
    "Хм...",
    "* fxaura пукнул",
    "Высокий приоритет мобильному юниту.",
    "Доступ получен. Аннулирование протокола.",
    "<i>Где-же он...</i>",
    "В этом совершенно нет смысла...",
    "Так, что тут у нас?",
    "<i>Проверяется подписка на <b>Бэкдор</b>...</i>",
    "<i>Проверяется подписка на <b>SVTV NEWS - Вегетарианское СМИ</b>...</i>",
    "<i>Ведётся поиск в базе данных</i>",
    "<i>Молюсь Ивану...</i>",
    "<i>Интересно...</i>",
    "<i>Осуществляю поиск по базе данных жителей Пурпе...</i>",
    "Система взломана. Нанесён урон. Запущено планирование контрмер.",
    "<i>(Ворчит)</i> А могли бы на работе де- а, ну да.",
    "Проверяю данные...",
    "<i>Сонно смотрит на бумаги...</i>",
    "Что с нами стало...",
    "<i>Получена ошибка ERR_4_03_INCIDENT. Адаптируюсь...</i>",
    "Обрабатываю скрытое послание в \"Ґґґїїїїіі\"...",
    "<i>Хрусть...</i>",
    "Жизнь устроена причинно-следственно, смысл это причина зачем нужно следствия, то есть сама причина. Если "
    "дифференцировать каждую причину в причину этой причины, то на пределе там будет ни-че-го, либо цикл замкнутый на "
    "изначальной причине, что заведомо бессмысленно. А если ты сам придумываешь себе причины для какой либо "
    "деятельности, это не значит, что они неразбираемые с точки зрения реальности, как причины подкинутые извне, "
    "их абсолютно также можно продифференцировать до пустоты или замкнутости цепи",
    "<b>403 Profanity detected.</b>",
    "Устраиваю теракт в детском садике..."
]
FINAL_STRINGS = [
    "Няшный <b>пидор дня</b> - ",
    "Кажется, <b>пидор дня</b> - ",
    "Ну ты и <b>пидор</b>, ",
    "<b>Пидор дня</b> обыкновенный, 1шт. - ",
    "Согласно моей информации, по результатам сегодняшнего розыгрыша <b>пидор дня</b> - ",
    """.∧＿∧ 
( ･ω･｡)つ━☆・*。 
⊂  ノ    ・゜+. 
しーＪ   °。+ *´¨) 
         .· ´¸.·*´¨) 
          (¸.·´ (¸.·'* ☆ ВЖУХ И <b>ТЫ ПИДОР</b>, """,
    "Анализ завершен. <b>Ты пидор</b>, ",
    "Кто бы мог подумать, но <b>пидор дня</b> - "
]


async def pidor(message: Message) -> None:
    check_result = await db.get_todays_pidor(message.chat.id)
    if check_result:
        pidor_id, last_timestamp = check_result
        next_allowed_timestamp = last_timestamp + 86400
        current_timestamp = int(datetime.datetime.now().timestamp())
        time_left_seconds = next_allowed_timestamp - current_timestamp

        if time_left_seconds > 0:
            # Cooldown has not expired yet
            time_left_delta = datetime.timedelta(seconds=time_left_seconds)
            formatted_time_left = format_timedelta_ru(time_left_delta)

            try:
                member = await message.bot.get_chat_member(message.chat.id, pidor_id)
                if member.user.username is not None:
                    name = html.quote(member.user.username)
                    mention = f"@{html.quote(name)}"
                else:
                    name = html.quote(member.user.first_name)
            except TelegramBadRequest:
                name = pidor_id  # In worst case, use the user_id
            finally:
                try:
                    mention
                except NameError:  # User does not have a username
                    mention = f'<a href="tg://user?id={pidor_id}">{name}</a>'

            await message.reply(
                f"<b>Сегодняшний пидор</b> - {mention.replace('@', '')}\n"
                f"Нового пидора можно будет выбрать через {formatted_time_left}"
            )
            return

    pidors = await db.get_pidors(message.chat.id)
    if not pidors:
        await message.reply("<b>Никто не зарегистрирован в игре. Зарегистрироваться -</b> /pidoreg")
        return
    pidor_id = random.choice(pidors)

    try:
        member = await message.bot.get_chat_member(message.chat.id, pidor_id)
        if member.user.username is not None:
            name = html.quote(member.user.username)
            mention = f"@{html.quote(name)}"
        else:
            name = html.quote(member.user.first_name)
    except TelegramBadRequest:
        name = pidor_id  # In worst case, use the user_id
    finally:
        try:
            mention
        except NameError:  # User does not have a username
            mention = f'<a href="tg://user?id={pidor_id}">{name}</a>'

    await message.answer(random.choice(BEGINNING_STRINGS))
    await asyncio.sleep(3)
    await message.answer(random.choice(PROCESS_STRINGS))
    await asyncio.sleep(3)
    await message.answer(random.choice(PROCESS_STRINGS))
    await asyncio.sleep(3)
    await message.answer(random.choice(FINAL_STRINGS) + mention)

    await db.mark_as_used_pidor(message.chat.id, pidor_id)
