# bot.py (полный код - только ввод номера в чат + кнопка смены языка, все 12 языков полностью)
import asyncio
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from config import Config
from utils import logger, normalize_phone
from checkers import PhoneChecker

# Тексты на 12 языках (полные версии)
TEXTS = {
    'ru': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Проверка номеров телефонов в реальном времени\n\n📱 *Как использовать:*\n• Просто *отправьте номер* в чат\n\nПримеры: `+71234567890` или `89123456789`\n\n🔍 *Проверяем через 5 API:*\n• Spravportal (спам)\n• Numverify (валидация)\n• Numlookup (геолокация)\n• Abstract (риск, утечки)\n• Vonage (оператор, портирование)\n\n🇷🇺 Поддерживаются: РФ, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Язык изменён на {}\n\nТеперь бот будет общаться с вами на этом языке.",
        'checking': "🔍 *Анализирую номер {}...*\n⏳ Проверка 5 баз данных\n⚡ 5-10 секунд",
        'invalid_format': "❌ *Неверный формат*\n\nОтправьте номер в формате:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Ошибка при проверке*\nПопробуйте позже",
        'tech_error': "⚠️ *Техническая ошибка*\nПопробуйте позже",
        'change_lang': "Сменить язык",
        'select_lang': "Выберите язык:",
        'danger_spam': "🚫 *ОПАСНОСТЬ! Номер в спам-базе* 🚫\n\n",
        'invalid_number': "⚠️ *Номер недействителен* ⚠️\n\n",
        'high_risk': "🔴 *ВЫСОКИЙ РИСК* 🔴\n\n",
        'breach_found': "📢 *Номер найден в утечках* 📢\n\n",
        'clean': "✅ *Номер чистый* ✅\n\n",
        'valid_yes': "✅ Да",
        'valid_no': "❌ Нет",
        'validity': "Валидность",
        'details_header': "┌─ 📊 *ДЕТАЛИ*",
        'carrier': "Оператор",
        'original_carrier': "Исходный оператор",
        'ported': "Портирован",
        'ported_yes': "перенесён",
        'ported_no': "не перенесён",
        'line_type': "Тип линии",
        'city': "Город",
        'region': "Регион",
        'roaming': "Роуминг",
        'roaming_active': "активен",
        'caller_name': "Владелец (CNAM)",
        'spam_categories': "🚨 *Категории спама:*",
        'risk': "🎲 *Риск:*",
        'temporary': "📱 *Временный/VOIP номер*",
        'breaches': "💥 *Утечки:*",
        'times': "раз(а)",
        'owner': "👤 *Владелец:*",
        'recommend_block': "🛑 *РЕКОМЕНДАЦИЯ: Заблокировать номер*",
        'recommend_ignore': "⚠️ *РЕКОМЕНДАЦИЯ: Не отвечать на звонки*",
        'recommend_use': "✨ *Номер можно использовать*"
    },
    'en': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Phone number verification in real time\n\n📱 *How to use:*\n• Simply *send the number* to the chat\n\nExamples: `+71234567890` or `89123456789`\n\n🔍 *Checking through 5 APIs:*\n• Spravportal (spam)\n• Numverify (validation)\n• Numlookup (geolocation)\n• Abstract (risk, breaches)\n• Vonage (carrier, porting)\n\n🌍 Supported countries: RU, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Language changed to {}\n\nThe bot will now communicate with you in this language.",
        'checking': "🔍 *Analyzing number {}...*\n⏳ Checking 5 databases\n⚡ 5-10 seconds",
        'invalid_format': "❌ *Invalid format*\n\nSend the number in format:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Check error*\nPlease try again later",
        'tech_error': "⚠️ *Technical error*\nPlease try again later",
        'change_lang': "Change language",
        'select_lang': "Select language:",
        'danger_spam': "🚫 *DANGER! Number in spam database* 🚫\n\n",
        'invalid_number': "⚠️ *Invalid number* ⚠️\n\n",
        'high_risk': "🔴 *HIGH RISK* 🔴\n\n",
        'breach_found': "📢 *Number found in data breaches* 📢\n\n",
        'clean': "✅ *Number is clean* ✅\n\n",
        'valid_yes': "✅ Yes",
        'valid_no': "❌ No",
        'validity': "Validity",
        'details_header': "┌─ 📊 *DETAILS*",
        'carrier': "Carrier",
        'original_carrier': "Original carrier",
        'ported': "Ported",
        'ported_yes': "ported",
        'ported_no': "not ported",
        'line_type': "Line type",
        'city': "City",
        'region': "Region",
        'roaming': "Roaming",
        'roaming_active': "active",
        'caller_name': "Owner (CNAM)",
        'spam_categories': "🚨 *Spam categories:*",
        'risk': "🎲 *Risk:*",
        'temporary': "📱 *Temporary/VOIP number*",
        'breaches': "💥 *Breaches:*",
        'times': "time(s)",
        'owner': "👤 *Owner:*",
        'recommend_block': "🛑 *RECOMMENDATION: Block the number*",
        'recommend_ignore': "⚠️ *RECOMMENDATION: Don't answer calls*",
        'recommend_use': "✨ *Number can be used*"
    },
    'kk': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Телефон нөмірлерін нақты уақытта тексеру\n\n📱 *Қалай пайдалану:*\n• Жай *нөмірді чатқа жіберіңіз*\n\nМысалдар: `+71234567890` немесе `89123456789`\n\n🔍 *5 API арқылы тексереміз:*\n• Spravportal (спам)\n• Numverify (валидация)\n• Numlookup (геолокация)\n• Abstract (қауіп, ағып кетулер)\n• Vonage (оператор, портирование)\n\n🇰🇿 Қолдау көрсетілетін елдер: РФ, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Тіл {} тіліне өзгертілді\n\nЕнді бот сізбен осы тілде сөйлеседі.",
        'checking': "🔍 *{} нөмірін талдау...*\n⏳ 5 дерекқорды тексеру\n⚡ 5-10 секунд",
        'invalid_format': "❌ *Қате формат*\n\nНөмірді келесі форматта жіберіңіз:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Тексеру қатесі*\nКейінірек қайталаңыз",
        'tech_error': "⚠️ *Техникалық қате*\nКейінірек қайталаңыз",
        'change_lang': "Тілді өзгерту",
        'select_lang': "Тілді таңдаңыз:",
        'danger_spam': "🚫 *ҚАУІП! Нөмір спам базасында* 🚫\n\n",
        'invalid_number': "⚠️ *Жарамсыз нөмір* ⚠️\n\n",
        'high_risk': "🔴 *ЖОҒАРЫ ҚАУІП* 🔴\n\n",
        'breach_found': "📢 *Нөмір деректер ағып кетулерінен табылды* 📢\n\n",
        'clean': "✅ *Нөмір таза* ✅\n\n",
        'valid_yes': "✅ Иә",
        'valid_no': "❌ Жоқ",
        'validity': "Жарамдылық",
        'details_header': "┌─ 📊 *ДЕРЕКТЕР*",
        'carrier': "Оператор",
        'original_carrier': "Бастапқы оператор",
        'ported': "Портирленген",
        'ported_yes': "портирленген",
        'ported_no': "портирленбеген",
        'line_type': "Желі түрі",
        'city': "Қала",
        'region': "Аймақ",
        'roaming': "Роуминг",
        'roaming_active': "белсенді",
        'caller_name': "Иесі (CNAM)",
        'spam_categories': "🚨 *Спам санаттары:*",
        'risk': "🎲 *Қауіп:*",
        'temporary': "📱 *Уақытша/VOIP нөмір*",
        'breaches': "💥 *Ағып кетулер:*",
        'times': "рет",
        'owner': "👤 *Иесі:*",
        'recommend_block': "🛑 *ҰСЫНЫС: Нөмірді бұғаттау*",
        'recommend_ignore': "⚠️ *ҰСЫНЫС: Қоңырауларға жауап бермеу*",
        'recommend_use': "✨ *Нөмірді пайдалануға болады*"
    },
    'uk': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Перевірка номерів телефонів у реальному часі\n\n📱 *Як використовувати:*\n• Просто *відправте номер* у чат\n\nПриклади: `+71234567890` або `89123456789`\n\n🔍 *Перевіряємо через 5 API:*\n• Spravportal (спам)\n• Numverify (валідація)\n• Numlookup (геолокація)\n• Abstract (ризик, витоки)\n• Vonage (оператор, портування)\n\n🇺🇦 Підтримуються: РФ, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Мову змінено на {}\n\nТепер бот спілкуватиметься з вами цією мовою.",
        'checking': "🔍 *Аналізую номер {}...*\n⏳ Перевірка 5 баз даних\n⚡ 5-10 секунд",
        'invalid_format': "❌ *Невірний формат*\n\nВідправте номер у форматі:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Помилка при перевірці*\nСпробуйте пізніше",
        'tech_error': "⚠️ *Технічна помилка*\nСпробуйте пізніше",
        'change_lang': "Змінити мову",
        'select_lang': "Виберіть мову:",
        'danger_spam': "🚫 *НЕБЕЗПЕКА! Номер у спам-базі* 🚫\n\n",
        'invalid_number': "⚠️ *Номер недійсний* ⚠️\n\n",
        'high_risk': "🔴 *ВИСОКИЙ РИЗИК* 🔴\n\n",
        'breach_found': "📢 *Номер знайдено у витоках* 📢\n\n",
        'clean': "✅ *Номер чистий* ✅\n\n",
        'valid_yes': "✅ Так",
        'valid_no': "❌ Ні",
        'validity': "Валідність",
        'details_header': "┌─ 📊 *ДЕТАЛІ*",
        'carrier': "Оператор",
        'original_carrier': "Початковий оператор",
        'ported': "Портований",
        'ported_yes': "портований",
        'ported_no': "не портований",
        'line_type': "Тип лінії",
        'city': "Місто",
        'region': "Регіон",
        'roaming': "Роумінг",
        'roaming_active': "активний",
        'caller_name': "Власник (CNAM)",
        'spam_categories': "🚨 *Категорії спаму:*",
        'risk': "🎲 *Ризик:*",
        'temporary': "📱 *Тимчасовий/VOIP номер*",
        'breaches': "💥 *Витоки:*",
        'times': "раз(и)",
        'owner': "👤 *Власник:*",
        'recommend_block': "🛑 *РЕКОМЕНДАЦІЯ: Заблокувати номер*",
        'recommend_ignore': "⚠️ *РЕКОМЕНДАЦІЯ: Не відповідати на дзвінки*",
        'recommend_use': "✨ *Номер можна використовувати*"
    },
    'be': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Праверка нумароў тэлефонаў у рэальным часе\n\n📱 *Як выкарыстоўваць:*\n• Проста *адпраўце нумар* у чат\n\nПрыклады: `+71234567890` або `89123456789`\n\n🔍 *Правяраем праз 5 API:*\n• Spravportal (спам)\n• Numverify (валідацыя)\n• Numlookup (геалакацыя)\n• Abstract (рызыка, уцечкі)\n• Vonage (аператар, партаванне)\n\n🇧🇾 Падтрымліваюцца: РФ, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Мова зменена на {}\n\nЦяпер бот будзе размаўляць з вамі на гэтай мове.",
        'checking': "🔍 *Аналізую нумар {}...*\n⏳ Праверка 5 баз даных\n⚡ 5-10 секунд",
        'invalid_format': "❌ *Няправільны фармат*\n\nАдпраўце нумар у фармаце:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Памылка пры праверцы*\nПаспрабуйце пазней",
        'tech_error': "⚠️ *Тэхнічная памылка*\nПаспрабуйце пазней",
        'change_lang': "Змяніць мову",
        'select_lang': "Абярыце мову:",
        'danger_spam': "🚫 *НЕБЯСПЕКА! Нумар у спам-базе* 🚫\n\n",
        'invalid_number': "⚠️ *Нумар несапраўдны* ⚠️\n\n",
        'high_risk': "🔴 *ВЫСОКІ РЫЗЫК* 🔴\n\n",
        'breach_found': "📢 *Нумар знойдзены ва ўцечках* 📢\n\n",
        'clean': "✅ *Нумар чысты* ✅\n\n",
        'valid_yes': "✅ Так",
        'valid_no': "❌ Не",
        'validity': "Валіднасць",
        'details_header': "┌─ 📊 *ДЭТАЛІ*",
        'carrier': "Аператар",
        'original_carrier': "Пачатковы аператар",
        'ported': "Партаваны",
        'ported_yes': "партаваны",
        'ported_no': "не партаваны",
        'line_type': "Тып лініі",
        'city': "Горад",
        'region': "Рэгіён",
        'roaming': "Роўмінг",
        'roaming_active': "актыўны",
        'caller_name': "Уладальнік (CNAM)",
        'spam_categories': "🚨 *Катэгорыі спаму:*",
        'risk': "🎲 *Рызык:*",
        'temporary': "📱 *Часовы/VOIP нумар*",
        'breaches': "💥 *Уцечкі:*",
        'times': "раз(ы)",
        'owner': "👤 *Уладальнік:*",
        'recommend_block': "🛑 *РЭКАМЕНДАЦЫЯ: Заблакіраваць нумар*",
        'recommend_ignore': "⚠️ *РЭКАМЕНДАЦЫЯ: Не адказваць на званкі*",
        'recommend_use': "✨ *Нумар можна выкарыстоўваць*"
    },
    'ky': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Телефон номерлерин реал убакытта текшерүү\n\n📱 *Кантип колдонуу:*\n• Жөн гана *номерди чатка жибериңиз*\n\nМисалдар: `+71234567890` же `89123456789`\n\n🔍 *5 API аркылуу текшеребиз:*\n• Spravportal (спам)\n• Numverify (валидация)\n• Numlookup (геолокация)\n• Abstract (тобокел, агып кетүүлөр)\n• Vonage (оператор, портирование)\n\n🇰🇬 Колдоого алынган өлкөлөр: РФ, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Тил {} тилине өзгөртүлдү\n\nЭми бот сиз менен ушул тилде сүйлөшөт.",
        'checking': "🔍 *{} номерин талдоо...*\n⏳ 5 маалымат базасын текшерүү\n⚡ 5-10 секунд",
        'invalid_format': "❌ *Ката формат*\n\nНомерди төмөнкү форматта жибериңиз:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Текшерүү катасы*\nКийинчерээк аракет кылыңыз",
        'tech_error': "⚠️ *Техникалык ката*\nКийинчерээк аракет кылыңыз",
        'change_lang': "Тилди өзгөртүү",
        'select_lang': "Тилди тандаңыз:",
        'danger_spam': "🚫 *КОРКУНУЧ! Номер спам базасында* 🚫\n\n",
        'invalid_number': "⚠️ *Жараксыз номер* ⚠️\n\n",
        'high_risk': "🔴 *ЖОГОРКУ ТОБОКЕЛ* 🔴\n\n",
        'breach_found': "📢 *Номер маалыматтардын агып кетүүсүнөн табылды* 📢\n\n",
        'clean': "✅ *Номер таза* ✅\n\n",
        'valid_yes': "✅ Ооба",
        'valid_no': "❌ Жок",
        'validity': "Жарактуулук",
        'details_header': "┌─ 📊 *МААЛЫМАТТАР*",
        'carrier': "Оператор",
        'original_carrier': "Баштапкы оператор",
        'ported': "Портирленген",
        'ported_yes': "портирленген",
        'ported_no': "портирленбеген",
        'line_type': "Байланыш түрү",
        'city': "Шаар",
        'region': "Аймак",
        'roaming': "Роуминг",
        'roaming_active': "активдүү",
        'caller_name': "Ээси (CNAM)",
        'spam_categories': "🚨 *Спам категориялары:*",
        'risk': "🎲 *Тобокел:*",
        'temporary': "📱 *Убактылуу/VOIP номер*",
        'breaches': "💥 *Агып кетүүлөр:*",
        'times': "жолу",
        'owner': "👤 *Ээси:*",
        'recommend_block': "🛑 *СУНУШ: Номерди бөгөттөө*",
        'recommend_ignore': "⚠️ *СУНУШ: Чалууларга жооп бербөө*",
        'recommend_use': "✨ *Номерди колдонсо болот*"
    },
    'tg': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Санҷиши рақамҳои телефон дар вақти воқеӣ\n\n📱 *Тарзи истифода:*\n• Танҳо *рақамро ба чат фиристед*\n\nНамунаҳо: `+71234567890` ё `89123456789`\n\n🔍 *Тавассути 5 API санҷиш мекунем:*\n• Spravportal (спам)\n• Numverify (валидатсия)\n• Numlookup (геолокатсия)\n• Abstract (хатар, ихроҷҳо)\n• Vonage (оператор, портирование)\n\n🇹🇯 Дастгиршаванда: РФ, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Забон ба {} тағйир ёфт\n\nАкнун бот бо шумо ба ин забон ҳарф мезанад.",
        'checking': "🔍 *Рақами {} таҳлил карда мешавад...*\n⏳ Санҷиши 5 пойгоҳи додаҳо\n⚡ 5-10 сония",
        'invalid_format': "❌ *Формати нодуруст*\n\nРақамро дар формат фиристед:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Хатогӣ ҳангоми санҷиш*\nБаъдтар аз нав кӯшиш кунед",
        'tech_error': "⚠️ *Хатогии техникӣ*\nБаъдтар аз нав кӯшиш кунед",
        'change_lang': "Иваз кардани забон",
        'select_lang': "Забонро интихоб кунед:",
        'danger_spam': "🚫 *ХАТАР! Рақам дар пойгоҳи спам* 🚫\n\n",
        'invalid_number': "⚠️ *Рақами беэътибор* ⚠️\n\n",
        'high_risk': "🔴 *ХАТАРИ БАЛАНД* 🔴\n\n",
        'breach_found': "📢 *Рақам дар ихроҷҳо ёфт шуд* 📢\n\n",
        'clean': "✅ *Рақам тоза аст* ✅\n\n",
        'valid_yes': "✅ Ҳа",
        'valid_no': "❌ Не",
        'validity': "Эътибор",
        'details_header': "┌─ 📊 *ТАФСИЛОТ*",
        'carrier': "Оператор",
        'original_carrier': "Оператори аслӣ",
        'ported': "Портирование шудааст",
        'ported_yes': "портирование шудааст",
        'ported_no': "портирование нашудааст",
        'line_type': "Намуди хат",
        'city': "Шаҳр",
        'region': "Минтақа",
        'roaming': "Роуминг",
        'roaming_active': "фаъол",
        'caller_name': "Соҳиб (CNAM)",
        'spam_categories': "🚨 *Категорияҳои спам:*",
        'risk': "🎲 *Хатар:*",
        'temporary': "📱 *Рақами муваққатӣ/VOIP*",
        'breaches': "💥 *Ихроҷҳо:*",
        'times': "марта",
        'owner': "👤 *Соҳиб:*",
        'recommend_block': "🛑 *ТАВСИЯ: Рақамро блок кунед*",
        'recommend_ignore': "⚠️ *ТАВСИЯ: Ба зангҳо ҷавоб надиҳед*",
        'recommend_use': "✨ *Рақамро истифода бурдан мумкин аст*"
    },
    'tk': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Telefon nomerlerini hakyky wagtda barlamak\n\n📱 *Nädip ulanmaly:*\n• Diňe *nomäri çata iberiň*\n\nMysallar: `+71234567890` ýa-da `89123456789`\n\n🔍 *5 API arkaly barlaýarys:*\n• Spravportal (spam)\n• Numverify (validasiýa)\n• Numlookup (geolokasiýa)\n• Abstract (howp, akymlar)\n• Vonage (operator, portirleme)\n\n🇹🇲 Goldanylýan ýurtlar: RF, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Dil {} diline üýtgedildi\n\nIndi bot size bu dilde gürleşer.",
        'checking': "🔍 *{} nomeri derňelýär...*\n⏳ 5 maglumat bazasyny barlamak\n⚡ 5-10 sekunt",
        'invalid_format': "❌ *Nädogry format*\n\nNomäri formatda iberiň:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Barlamakda säwlik*\nSoňra gaýtadan synanyşyň",
        'tech_error': "⚠️ *Tehniki säwlik*\nSoňra gaýtadan synanyşyň",
        'change_lang': "Dili üýtgetmek",
        'select_lang': "Dili saýlaň:",
        'danger_spam': "🚫 *HOWP! Nomer spam bazasynda* 🚫\n\n",
        'invalid_number': "⚠️ *Nomer ygtybarly däl* ⚠️\n\n",
        'high_risk': "🔴 *ÝOKARY HOWP* 🔴\n\n",
        'breach_found': "📢 *Nomer maglumat akymlarynda tapyldy* 📢\n\n",
        'clean': "✅ *Nomer arassa* ✅\n\n",
        'valid_yes': "✅ Hawa",
        'valid_no': "❌ Ýok",
        'validity': "Ygtybarlylyk",
        'details_header': "┌─ 📊 *JIKA-JIKLAR*",
        'carrier': "Operator",
        'original_carrier': "Asyl operator",
        'ported': "Portirlen",
        'ported_yes': "portirlen",
        'ported_no': "portirlenmedik",
        'line_type': "Liniýa görnüşi",
        'city': "Şäher",
        'region': "Sebit",
        'roaming': "Rouming",
        'roaming_active': "işjeň",
        'caller_name': "Eýesi (CNAM)",
        'spam_categories': "🚨 *Spam kategoriýalary:*",
        'risk': "🎲 *Howp:*",
        'temporary': "📱 *Wagtlaýyn/VOIP nomer*",
        'breaches': "💥 *Akymlar:*",
        'times': "gezek",
        'owner': "👤 *Eýesi:*",
        'recommend_block': "🛑 *TEKLIP: Nomeri bloklaň*",
        'recommend_ignore': "⚠️ *TEKLIP: Jaňlara jogap bermäň*",
        'recommend_use': "✨ *Nomeri ulanmak bolýar*"
    },
    'uz': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Telefon raqamlarini real vaqtda tekshirish\n\n📱 *Qanday ishlatish:*\n• Shunchaki *raqamni chatga yuboring*\n\nMisollar: `+71234567890` yoki `89123456789`\n\n🔍 *5 API orqali tekshiramiz:*\n• Spravportal (spam)\n• Numverify (validatsiya)\n• Numlookup (geolokatsiya)\n• Abstract (xavf, oqmalar)\n• Vonage (operator, portlash)\n\n🇺🇿 Qo'llab-quvvatlanadigan davlatlar: RF, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Til {} ga o'zgartirildi\n\nEndi bot siz bilan bu tilda gaplashadi.",
        'checking': "🔍 *{} raqami tahlil qilinmoqda...*\n⏳ 5 ma'lumotlar bazasini tekshirish\n⚡ 5-10 soniya",
        'invalid_format': "❌ *Noto'g'ri format*\n\nRaqamni formatda yuboring:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Tekshirishda xatolik*\nKeyinroq urinib ko'ring",
        'tech_error': "⚠️ *Texnik xatolik*\nKeyinroq urinib ko'ring",
        'change_lang': "Tilni o'zgartirish",
        'select_lang': "Tilni tanlang:",
        'danger_spam': "🚫 *XAVF! Raqam spam bazasida* 🚫\n\n",
        'invalid_number': "⚠️ *Yaroqsiz raqam* ⚠️\n\n",
        'high_risk': "🔴 *YUQORI XAVF* 🔴\n\n",
        'breach_found': "📢 *Raqam ma'lumotlar oqmasidan topildi* 📢\n\n",
        'clean': "✅ *Raqam toza* ✅\n\n",
        'valid_yes': "✅ Ha",
        'valid_no': "❌ Yo'q",
        'validity': "Haqiqiylik",
        'details_header': "┌─ 📊 *MA'LUMOTLAR*",
        'carrier': "Operator",
        'original_carrier': "Asl operator",
        'ported': "Portlangan",
        'ported_yes': "portlangan",
        'ported_no': "portlanmagan",
        'line_type': "Liniya turi",
        'city': "Shahar",
        'region': "Hudud",
        'roaming': "Rouming",
        'roaming_active': "faol",
        'caller_name': "Egasi (CNAM)",
        'spam_categories': "🚨 *Spam kategoriyalari:*",
        'risk': "🎲 *Xavf:*",
        'temporary': "📱 *Vaqtinchalik/VOIP raqam*",
        'breaches': "💥 *Oqmalar:*",
        'times': "marta",
        'owner': "👤 *Egasi:*",
        'recommend_block': "🛑 *TAVSIYA: Raqamni bloklang*",
        'recommend_ignore': "⚠️ *TAVSIYA: Qo'ng'iroqlarga javob bermang*",
        'recommend_use': "✨ *Raqamdan foydalanish mumkin*"
    },
    'az': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Telefon nömrələrinin real vaxtda yoxlanılması\n\n📱 *Necə istifadə etməli:*\n• Sadəcə *nömrəni çata göndərin*\n\nNümunələr: `+71234567890` və ya `89123456789`\n\n🔍 *5 API vasitəsilə yoxlayırıq:*\n• Spravportal (spam)\n• Numverify (validasiya)\n• Numlookup (geolokasiya)\n• Abstract (risk, sızmalar)\n• Vonage (operator, portlaşdırma)\n\n🇦🇿 Dəstəklənən ölkələr: RF, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Dil {} olaraq dəyişdirildi\n\nİndi bot sizinlə bu dildə danışacaq.",
        'checking': "🔍 *{} nömrəsi analiz edilir...*\n⏳ 5 məlumat bazası yoxlanılır\n⚡ 5-10 saniyə",
        'invalid_format': "❌ *Yanlış format*\n\nNömrəni formatda göndərin:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Yoxlamada xəta*\nDaha sonra təkrar edin",
        'tech_error': "⚠️ *Texniki xəta*\nDaha sonra təkrar edin",
        'change_lang': "Dili dəyişdir",
        'select_lang': "Dili seçin:",
        'danger_spam': "🚫 *TƏHLÜKƏ! Nömrə spam bazasında* 🚫\n\n",
        'invalid_number': "⚠️ *Etibarsız nömrə* ⚠️\n\n",
        'high_risk': "🔴 *YÜKSƏK RİSK* 🔴\n\n",
        'breach_found': "📢 *Nömrə məlumat sızmalarında tapıldı* 📢\n\n",
        'clean': "✅ *Nömrə təmizdir* ✅\n\n",
        'valid_yes': "✅ Bəli",
        'valid_no': "❌ Xeyr",
        'validity': "Etibarlılıq",
        'details_header': "┌─ 📊 *TƏFƏRRÜATLAR*",
        'carrier': "Operator",
        'original_carrier': "İlkin operator",
        'ported': "Portlaşdırılıb",
        'ported_yes': "portlaşdırılıb",
        'ported_no': "portlaşdırılmayıb",
        'line_type': "Xətt növü",
        'city': "Şəhər",
        'region': "Region",
        'roaming': "Rouminq",
        'roaming_active': "aktiv",
        'caller_name': "Sahibi (CNAM)",
        'spam_categories': "🚨 *Spam kateqoriyaları:*",
        'risk': "🎲 *Risk:*",
        'temporary': "📱 *Müvəqqəti/VOIP nömrə*",
        'breaches': "💥 *Sızmalar:*",
        'times': "dəfə",
        'owner': "👤 *Sahibi:*",
        'recommend_block': "🛑 *TÖVSİYƏ: Nömrəni bloklayın*",
        'recommend_ignore': "⚠️ *TÖVSİYƏ: Zənglərə cavab verməyin*",
        'recommend_use': "✨ *Nömrədən istifadə etmək olar*"
    },
    'ka': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ ტელეფონის ნომრების რეალურ დროში შემოწმება\n\n📱 *როგორ გამოვიყენოთ:*\n• უბრალოდ *გაგზავნეთ ნომერი* ჩატში\n\nმაგალითები: `+71234567890` ან `89123456789`\n\n🔍 *ვამოწმებთ 5 API-ით:*\n• Spravportal (სპამი)\n• Numverify (ვალიდაცია)\n• Numlookup (გეოლოკაცია)\n• Abstract (რისკი, გაჟონვები)\n• Vonage (ოპერატორი, პორტირება)\n\n🇬🇪 მხარდაჭერილი ქვეყნები: RF, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ ენა შეიცვალა {}\n\nახლა ბოტი ამ ენაზე გელაპარაკებით.",
        'checking': "🔍 *{} ნომრის ანალიზი...*\n⏳ 5 მონაცემთა ბაზის შემოწმება\n⚡ 5-10 წამი",
        'invalid_format': "❌ *არასწორი ფორმატი*\n\nგაგზავნეთ ნომერი ფორმატში:\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *შემოწმების შეცდომა*\nმოგვიანებით სცადეთ",
        'tech_error': "⚠️ *ტექნიკური შეცდომა*\nმოგვიანებით სცადეთ",
        'change_lang': "ენის შეცვლა",
        'select_lang': "აირჩიეთ ენა:",
        'danger_spam': "🚫 *საშიშროება! ნომერი სპამ-ბაზაშია* 🚫\n\n",
        'invalid_number': "⚠️ *არამოქმედი ნომერი* ⚠️\n\n",
        'high_risk': "🔴 *მაღალი რისკი* 🔴\n\n",
        'breach_found': "📢 *ნომერი ნაპოვნია გაჟონვებში* 📢\n\n",
        'clean': "✅ *ნომერი სუფთაა* ✅\n\n",
        'valid_yes': "✅ დიახ",
        'valid_no': "❌ არა",
        'validity': "ვალიდურობა",
        'details_header': "┌─ 📊 *დეტალები*",
        'carrier': "ოპერატორი",
        'original_carrier': "თავდაპირველი ოპერატორი",
        'ported': "პორტირებული",
        'ported_yes': "პორტირებული",
        'ported_no': "არაა პორტირებული",
        'line_type': "ხაზის ტიპი",
        'city': "ქალაქი",
        'region': "რეგიონი",
        'roaming': "როუმინგი",
        'roaming_active': "აქტიური",
        'caller_name': "მფლობელი (CNAM)",
        'spam_categories': "🚨 *სპამის კატეგორიები:*",
        'risk': "🎲 *რისკი:*",
        'temporary': "📱 *დროებითი/VOIP ნომერი*",
        'breaches': "💥 *გაჟონვები:*",
        'times': "ჯერ",
        'owner': "👤 *მფლობელი:*",
        'recommend_block': "🛑 *რეკომენდაცია: დაბლოკეთ ნომერი*",
        'recommend_ignore': "⚠️ *რეკომენდაცია: ნუ უპასუხებთ ზარებს*",
        'recommend_use': "✨ *ნომრის გამოყენება შეიძლება*"
    },
    'hy': {
        'welcome': "🌟 *PhoneGuard Bot* 🌟\n\n🛡️ Հեռախոսահամարների ստուգում իրական ժամանակում\n\n📱 *Ինչպես օգտագործել:*\n• Պարզապես *ուղարկեք համարը* զրույցում\n\nՕրինակներ՝ `+71234567890` կամ `89123456789`\n\n🔍 *Ստուգում ենք 5 API-ներով:*\n• Spravportal (սպամ)\n• Numverify (վալիդացիա)\n• Numlookup (աշխարհագրություն)\n• Abstract (ռիսկ, արտահոսքեր)\n• Vonage (օպերատոր, պորտավորում)\n\n🇦🇲 Աջակցվող երկրներ՝ RF, KZ, UA, BY, KG, TJ, TM, UZ, AZ, GE, AM, MD",
        'language_changed': "✅ Լեզուն փոխվեց {}\n\nԱյժմ բոտը ձեզ հետ կխոսի այս լեզվով։",
        'checking': "🔍 *{} համարի վերլուծություն...*\n⏳ 5 տվյալների բազաների ստուգում\n⚡ 5-10 վայրկյան",
        'invalid_format': "❌ *Սխալ ձևաչափ*\n\nՈւղարկեք համարը ձևաչափով՝\n• `+71234567890`\n• `89123456789`",
        'error': "❌ *Ստուգման սխալ*\nՓորձեք ավելի ուշ",
        'tech_error': "⚠️ *Տեխնիկական սխալ*\nՓորձեք ավելի ուշ",
        'change_lang': "Փոխել լեզուն",
        'select_lang': "Ընտրեք լեզուն:",
        'danger_spam': "🚫 *ՎՏԱՆԳ! Համարը սպամ-բազայում է* 🚫\n\n",
        'invalid_number': "⚠️ *Անվավեր համար* ⚠️\n\n",
        'high_risk': "🔴 *ԲԱՐՁՐ ՌԻՍԿ* 🔴\n\n",
        'breach_found': "📢 *Համարը գտնվել է արտահոսքերում* 📢\n\n",
        'clean': "✅ *Համարը մաքուր է* ✅\n\n",
        'valid_yes': "✅ Այո",
        'valid_no': "❌ Ոչ",
        'validity': "Վավերականություն",
        'details_header': "┌─ 📊 *ՄԱՆՐԱՄԱՍՆԵՐ*",
        'carrier': "Օպերատոր",
        'original_carrier': "Սկզբնական օպերատոր",
        'ported': "Պորտավորված",
        'ported_yes': "պորտավորված",
        'ported_no': "չի պորտավորվել",
        'line_type': "Գծի տեսակ",
        'city': "Քաղաք",
        'region': "Մարզ",
        'roaming': "Ռոումինգ",
        'roaming_active': "ակտիվ",
        'caller_name': "Սեփականատեր (CNAM)",
        'spam_categories': "🚨 *Սպամի կատեգորիաներ:*",
        'risk': "🎲 *Ռիսկ:*",
        'temporary': "📱 *Ժամանակավոր/VOIP համար*",
        'breaches': "💥 *Արտահոսքեր:*",
        'times': "անգամ",
        'owner': "👤 *Սեփականատեր:*",
        'recommend_block': "🛑 *ԱՌԱՋԱՐԿՈՒԹՅՈՒՆ: Արգելափակել համարը*",
        'recommend_ignore': "⚠️ *ԱՌԱՋԱՐԿՈՒԹՅՈՒՆ: Մի պատասխանեք զանգերին*",
        'recommend_use': "✨ *Համարը կարելի է օգտագործել*"
    }
}

# Доступные языки с флагами
LANGUAGES = {
    'ru': {'name': 'Русский', 'flag': '🇷🇺'},
    'en': {'name': 'English', 'flag': '🇬🇧'},
    'kk': {'name': 'Қазақша', 'flag': '🇰🇿'},
    'uk': {'name': 'Українська', 'flag': '🇺🇦'},
    'be': {'name': 'Беларуская', 'flag': '🇧🇾'},
    'ky': {'name': 'Кыргызча', 'flag': '🇰🇬'},
    'tg': {'name': 'Тоҷикӣ', 'flag': '🇹🇯'},
    'tk': {'name': 'Türkmençe', 'flag': '🇹🇲'},
    'uz': {'name': 'Oʻzbekcha', 'flag': '🇺🇿'},
    'az': {'name': 'Azərbaycanca', 'flag': '🇦🇿'},
    'ka': {'name': 'ქართული', 'flag': '🇬🇪'},
    'hy': {'name': 'Հայերեն', 'flag': '🇦🇲'}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = context.user_data.get('language', 'ru')
    text = TEXTS.get(user_lang, TEXTS['ru'])
    
    keyboard = [
        [InlineKeyboardButton("🌐 " + text['change_lang'], callback_data="change_language")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text['welcome'],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    row = []
    for i, (code, lang) in enumerate(LANGUAGES.items(), 1):
        row.append(InlineKeyboardButton(f"{lang['flag']} {lang['name']}", callback_data=f"lang_{code}"))
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    user_lang = context.user_data.get('language', 'ru')
    text = TEXTS.get(user_lang, TEXTS['ru'])
    
    await query.edit_message_text(
        "🌐 *" + text['select_lang'] + "*\n\n",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("lang_", "")
    context.user_data['language'] = lang_code
    text = TEXTS.get(lang_code, TEXTS['ru'])
    lang_name = LANGUAGES.get(lang_code, {}).get('name', lang_code)
    
    keyboard = [
        [InlineKeyboardButton("🌐 " + text['change_lang'], callback_data="change_language")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text['language_changed'].format(lang_name) + "\n\n" + text['welcome'],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def check_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = context.user_data.get('language', 'ru')
    text = TEXTS.get(user_lang, TEXTS['ru'])
    phone_raw = update.message.text.strip()
    
    status_msg = await update.message.reply_text(
        text['checking'].format(phone_raw),
        parse_mode=ParseMode.MARKDOWN
    )
    
    result = normalize_phone(phone_raw)
    if not result:
        await status_msg.edit_text(text['invalid_format'], parse_mode=ParseMode.MARKDOWN)
        return
    
    phone, country = result
    
    try:
        async with PhoneChecker(phone, country) as checker:
            report = await checker.check_all()
        
        if report.risk_level is None:
            report.risk_level = "unknown"
        if report.total_breaches is None:
            report.total_breaches = 0
        
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴", "unknown": "⚪"}
        
        if report.is_spam:
            header = text['danger_spam']
        elif not report.is_valid:
            header = text['invalid_number']
        elif report.risk_level == "high":
            header = text['high_risk']
        elif report.total_breaches > 0:
            header = text['breach_found']
        else:
            header = text['clean']
        
        message = header
        message += f"📞 `{report.phone}`\n"
        message += f"🌍 {report.country_name or country}\n\n"
        
        message += f"{text['details_header']}\n"
        message += f"├ {text['validity']}: {text['valid_yes'] if report.is_valid else text['valid_no']}\n"
        
        if report.carrier:
            message += f"├ {text['carrier']}: `{report.carrier}`\n"
        
        if report.original_carrier and report.original_carrier != report.carrier:
            message += f"├ {text['original_carrier']}: `{report.original_carrier}`\n"
        
        if report.ported and report.ported != "unknown":
            ported_emoji = "🔄" if report.ported == "ported" else "✅"
            ported_text_val = text['ported_yes'] if report.ported == "ported" else text['ported_no']
            message += f"├ {text['ported']}: {ported_emoji} `{ported_text_val}`\n"
        
        if report.line_type:
            line_emoji = "📱" if report.line_type == "mobile" else "🏠" if report.line_type == "landline" else "💻"
            message += f"├ {text['line_type']}: {line_emoji} `{report.line_type}`\n"
        
        if report.city or report.location:
            loc = report.city or report.location
            if loc:
                message += f"├ {text['city']}: 📍 `{loc}`\n"
        if report.region:
            message += f"├ {text['region']}: `{report.region}`\n"
        
        if report.roaming:
            message += f"├ {text['roaming']}: 🌍 `{text['roaming_active']}`\n"
        
        if report.caller_name:
            message += f"├ {text['caller_name']}: `{report.caller_name}`\n"
        
        message += "└────────────────\n\n"
        
        if report.is_spam and report.spam_categories:
            message += f"{text['spam_categories']}\n"
            for cat in report.spam_categories:
                if cat:
                    message += f"• `{cat}`\n"
            message += "\n"
        
        if report.risk_level and report.risk_level != "unknown":
            message += f"{text['risk']} {risk_emoji.get(report.risk_level, '⚪')} `{report.risk_level.upper()}`\n"
        
        if report.is_disposable:
            message += f"{text['temporary']}\n"
        
        if report.total_breaches > 0:
            message += f"\n{text['breaches']} {report.total_breaches} {text['times']}\n"
            if report.breach_domains and len(report.breach_domains) > 0:
                message += f"• {', '.join(report.breach_domains[:3])}\n"
        
        if report.registered_name:
            message += f"\n{text['owner']} `{report.registered_name}`"
            if report.registration_type:
                message += f" ({report.registration_type})"
            message += "\n"
        
        message += "\n" + "─" * 25 + "\n"
        message += f"📱 `{report.international_format or phone}`\n"
        if report.local_format:
            message += f"📞 `{report.local_format}`\n"
        
        if report.is_spam:
            message += f"\n{text['recommend_block']}"
        elif report.risk_level == "high":
            message += f"\n{text['recommend_ignore']}"
        elif report.is_valid:
            message += f"\n{text['recommend_use']}"
        
        keyboard = [
            [InlineKeyboardButton("🌐 " + text['change_lang'], callback_data="change_language")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await status_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in check_phone: {e}")
        await status_msg.edit_text(text['error'], parse_mode=ParseMode.MARKDOWN)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        user_lang = context.user_data.get('language', 'ru')
        text = TEXTS.get(user_lang, TEXTS['ru'])
        await update.effective_message.reply_text(
            text['tech_error'],
            parse_mode=ParseMode.MARKDOWN
        )

def main():
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(change_language, pattern="change_language"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_phone))
    app.add_error_handler(error_handler)
    
    logger.info("🚀 PhoneGuard Bot started with 5 APIs and 12 languages!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
