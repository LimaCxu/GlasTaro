import os
import logging
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from dotenv import load_dotenv
from src.tarot_reader import TarotReader
from src.language_manager import language_manager
from data.tarot_cards import MAJOR_ARCANA, MINOR_ARCANA

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TarotBot:
    def __init__(self):
        self.tarot_reader = TarotReader()
        self.user_sessions = {}  # 存储用户会话数据
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.effective_user
        user_id = user.id
        
        welcome_text = language_manager.get_text(user_id, 'welcome', name=user.first_name)
        
        keyboard = [
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_reading'), callback_data="start_reading")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_daily'), callback_data="daily_card")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_learn'), callback_data="learn_tarot")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_language'), callback_data="language_select")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_help'), callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        user_id = update.effective_user.id
        help_text = language_manager.get_text(user_id, 'help_text')
        await update.message.reply_text(help_text)
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /language 命令"""
        await self.show_language_options(update, context)
    
    async def daily_card_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /daily 命令"""
        await self.send_daily_card(update, context)
    
    async def reading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /reading 命令"""
        await self.show_spread_options(update, context)
    
    async def learn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /learn 命令"""
        await self.show_learning_options(update, context)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮回调"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        if data == "start_reading":
            await self.show_spread_options(update, context)
        elif data == "daily_card":
            await self.send_daily_card(update, context)
        elif data == "learn_tarot":
            await self.show_learning_options(update, context)
        elif data == "language_select":
            await self.show_language_options(update, context)
        elif data.startswith("lang_"):
            language = data.replace("lang_", "")
            await self.set_user_language(update, context, language)
        elif data == "help":
            await self.show_help(update, context)
        elif data.startswith("spread_"):
            spread_type = data.replace("spread_", "")
            await self.ask_question(update, context, spread_type)
        elif data.startswith("learn_"):
            learn_type = data.replace("learn_", "")
            await self.show_card_category(update, context, learn_type)
        elif data.startswith("card_"):
            card_id = data.replace("card_", "")
            await self.show_card_explanation(update, context, card_id)
        elif data.startswith("skip_question_"):
            spread_type = data.replace("skip_question_", "")
            await self.perform_reading(update, context, spread_type)
        elif data == "back_to_main":
            await self.show_main_menu(update, context)
        elif data == "back_to_spreads":
            await self.show_spread_options(update, context)
        elif data == "back_to_learning":
            await self.show_learning_options(update, context)
    
    async def show_language_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """显示语言选择选项"""
        user_id = update.effective_user.id
        text = language_manager.get_text(user_id, 'language_select')
        
        keyboard = []
        for lang_code, lang_name in language_manager.get_supported_languages().items():
            keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")])
        
        keyboard.append([InlineKeyboardButton(language_manager.get_text(user_id, 'back_main'), callback_data="back_to_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def set_user_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """设置用户语言"""
        user_id = update.effective_user.id
        
        if language_manager.set_user_language(user_id, language):
            success_text = language_manager.get_text(user_id, 'language_changed')
            await update.callback_query.edit_message_text(success_text)
            
            # 延迟显示主菜单
            import asyncio
            await asyncio.sleep(1)
            await self.show_main_menu(update, context)
        else:
            error_text = language_manager.get_text(user_id, 'error_general')
            await update.callback_query.edit_message_text(error_text)
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """显示主菜单"""
        user = update.effective_user
        user_id = user.id
        
        welcome_text = language_manager.get_text(user_id, 'welcome', name=user.first_name)
        
        keyboard = [
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_reading'), callback_data="start_reading")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_daily'), callback_data="daily_card")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_learn'), callback_data="learn_tarot")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_language'), callback_data="language_select")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_help'), callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def show_spread_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """显示牌阵选项"""
        user_id = update.effective_user.id
        text = language_manager.get_text(user_id, 'spread_select')
        
        keyboard = [
            [InlineKeyboardButton(language_manager.get_text(user_id, 'spread_single'), callback_data="spread_single")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'spread_three'), callback_data="spread_three_card")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'spread_love'), callback_data="spread_love")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'spread_career'), callback_data="spread_career")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'spread_decision'), callback_data="spread_decision")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'back_main'), callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def ask_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, spread_type: str):
        """询问用户问题"""
        user_id = update.effective_user.id
        self.user_sessions[user_id] = {'spread_type': spread_type, 'waiting_for_question': True}
        
        spread_name = language_manager.get_spread_name(user_id, spread_type)
        text = language_manager.get_text(user_id, 'ask_question', spread_name=spread_name)
        
        keyboard = [
            [InlineKeyboardButton(language_manager.get_text(user_id, 'skip_question'), callback_data=f"skip_question_{spread_type}")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'back_spreads'), callback_data="back_to_spreads")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理用户输入的问题"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions or not self.user_sessions[user_id].get('waiting_for_question'):
            return
        
        question = update.message.text
        spread_type = self.user_sessions[user_id]['spread_type']
        
        # 清除会话状态
        self.user_sessions[user_id]['waiting_for_question'] = False
        
        await self.perform_reading(update, context, spread_type, question)
    
    async def perform_reading(self, update: Update, context: ContextTypes.DEFAULT_TYPE, spread_type: str, question: str = None):
        """执行塔罗占卜"""
        user_id = update.effective_user.id
        
        # 发送"正在占卜"消息
        loading_text = language_manager.get_text(user_id, 'reading_loading')
        
        if update.callback_query:
            loading_msg = await update.callback_query.message.reply_text(loading_text)
        else:
            loading_msg = await update.message.reply_text(loading_text)
        
        try:
            # 根据牌阵类型确定抽牌数量
            num_cards = 1 if spread_type == "single" else 3
            
            # 抽取塔罗牌
            cards = self.tarot_reader.draw_cards(num_cards)
            
            # 生成解读
            reading = self.tarot_reader.get_reading(cards, question, spread_type, user_id)
            
            # 格式化结果
            result_text = self.format_reading_result(cards, reading, question, spread_type, user_id)
            
            # 删除加载消息并发送结果
            await loading_msg.delete()
            
            keyboard = [
                [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_reading'), callback_data="start_reading")],
                [InlineKeyboardButton(language_manager.get_text(user_id, 'back_main'), callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            await loading_msg.delete()
            error_text = language_manager.get_text(user_id, 'error_general')
            if update.callback_query:
                await update.callback_query.message.reply_text(f"{error_text}: {str(e)}")
            else:
                await update.message.reply_text(f"{error_text}: {str(e)}")
    
    def format_reading_result(self, cards: List[Dict], reading: str, question: str, spread_type: str, user_id: int) -> str:
        """格式化占卜结果"""
        spread_name = language_manager.get_spread_name(user_id, spread_type)
        user_language = language_manager.get_user_language(user_id)
        
        # 多语言文本
        result_title = {
            'zh': f"🔮 *{spread_name}结果*\n\n",
            'en': f"🔮 *{spread_name} Result*\n\n",
            'ru': f"🔮 *Результат {spread_name}*\n\n"
        }
        
        question_label = {
            'zh': "❓ *问题：*",
            'en': "❓ *Question:*",
            'ru': "❓ *Вопрос:*"
        }
        
        cards_label = {
            'zh': "🎴 *抽取的牌：*\n",
            'en': "🎴 *Drawn Cards:*\n",
            'ru': "🎴 *Вытянутые карты:*\n"
        }
        
        reading_label = {
            'zh': "📖 *解读：*\n",
            'en': "📖 *Reading:*\n",
            'ru': "📖 *Толкование:*\n"
        }
        
        blessing = {
            'zh': "✨ _愿塔罗的智慧为你指引方向_",
            'en': "✨ _May the wisdom of Tarot guide your way_",
            'ru': "✨ _Пусть мудрость Таро направляет ваш путь_"
        }
        
        result = result_title.get(user_language, result_title['zh'])
        
        if question and question not in ["跳过", "skip", "пропустить"]:
            result += f"{question_label.get(user_language, question_label['zh'])} {question}\n\n"
        
        result += cards_label.get(user_language, cards_label['zh'])
        for i, card in enumerate(cards, 1):
            orientation_emoji = "⬆️" if card['orientation'] in ['正位', 'upright', 'прямое'] else "⬇️"
            result += f"{i}. {orientation_emoji} {card['name']} ({card['orientation']})\n"
        
        result += f"\n{reading_label.get(user_language, reading_label['zh'])}{reading}\n\n"
        result += blessing.get(user_language, blessing['zh'])
        
        return result
    
    async def send_daily_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """发送每日塔罗牌"""
        try:
            user_id = update.effective_user.id
            
            # 获取每日塔罗牌
            card, reading = self.tarot_reader.get_daily_card(user_id)
            
            orientation_emoji = "⬆️" if card['orientation'] == '正位' else "⬇️"
            
            # 获取多语言文本
            daily_title = language_manager.get_text(user_id, 'daily_title')
            today_card_label = language_manager.get_text(user_id, 'today_card')
            guidance_label = language_manager.get_text(user_id, 'guidance')
            blessing = language_manager.get_text(user_id, 'daily_blessing')
            start_reading_text = language_manager.get_text(user_id, 'menu_reading')
            back_main_text = language_manager.get_text(user_id, 'back_main')
            
            text = f"""
🌅 *{daily_title}*

🎴 *{today_card_label}：*
{orientation_emoji} {card['name']} ({card['orientation']})

📖 *{guidance_label}：*
{reading}

✨ _{blessing}_
            """
            
            keyboard = [
                [InlineKeyboardButton(f"🔮 {start_reading_text}", callback_data="start_reading")],
                [InlineKeyboardButton(f"🏠 {back_main_text}", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            user_id = update.effective_user.id
            error_text = language_manager.get_text(user_id, 'error_general')
            if update.callback_query:
                await update.callback_query.edit_message_text(f"{error_text}: {str(e)}")
            else:
                await update.message.reply_text(f"{error_text}: {str(e)}")
    
    async def show_learning_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """显示学习选项"""
        user_id = update.effective_user.id
        
        text = language_manager.get_text(user_id, 'learning_center')
        
        keyboard = [
            [InlineKeyboardButton(language_manager.get_text(user_id, 'learn_major'), callback_data="learn_major")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'learn_minor'), callback_data="learn_minor")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'learn_basics'), callback_data="learn_basics")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'back_main'), callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def show_card_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
        """显示塔罗牌分类"""
        user_id = update.effective_user.id
        
        if category == "major":
            title = language_manager.get_text(user_id, 'learn_major')
            description = language_manager.get_text(user_id, 'major_description')
            text = f"🌟 *{title}*\n\n{description}"
            cards = [(f"major_{i}", info['name']) for i, info in MAJOR_ARCANA.items()]
        elif category == "minor":
            title = language_manager.get_text(user_id, 'learn_minor')
            description = language_manager.get_text(user_id, 'minor_description')
            text = f"🎴 *{title}*\n\n{description}"
            cards = []
            for suit, suit_info in MINOR_ARCANA.items():
                for card_name, card_info in suit_info['cards'].items():
                    cards.append((f"{suit}_{card_name}", card_info['name']))
        elif category == "basics":
            await self.show_tarot_basics(update, context)
            return
        else:
            return
        
        # 分页显示牌（每页10张）
        page_size = 10
        total_pages = (len(cards) + page_size - 1) // page_size
        
        keyboard = []
        for i in range(0, min(page_size, len(cards))):
            card_id, card_name = cards[i]
            keyboard.append([InlineKeyboardButton(card_name, callback_data=f"card_{card_id}")])
        
        if total_pages > 1:
            next_page_text = language_manager.get_text(user_id, 'next_page')
            keyboard.append([InlineKeyboardButton(f"➡️ {next_page_text}", callback_data=f"page_{category}_1")])
        
        back_to_learning_text = language_manager.get_text(user_id, 'back_learning')
        keyboard.append([InlineKeyboardButton(f"🔙 {back_to_learning_text}", callback_data="back_to_learning")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_card_explanation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, card_id: str):
        """显示塔罗牌详细解释"""
        user_id = update.effective_user.id
        
        try:
            card, explanation = self.tarot_reader.get_card_explanation(card_id)
            
            if not card:
                error_text = language_manager.get_text(user_id, 'card_not_found')
                await update.callback_query.edit_message_text(error_text)
                return
            
            text = f"🎴 *{card['name']}*\n\n{explanation}"
            
            back_to_list_text = language_manager.get_text(user_id, 'back_list')
            back_main_text = language_manager.get_text(user_id, 'back_main')
            
            keyboard = [
                [InlineKeyboardButton(f"🔙 {back_to_list_text}", callback_data=f"learn_{'major' if card['type'] == 'major' else 'minor'}")],
                [InlineKeyboardButton(f"🏠 {back_main_text}", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            error_text = language_manager.get_text(user_id, 'error_general')
            await update.callback_query.edit_message_text(f"{error_text}: {str(e)}")
    
    async def show_tarot_basics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """显示塔罗基础知识"""
        user_id = update.effective_user.id
        
        text = language_manager.get_text(user_id, 'tarot_basics')
        
        back_to_learning_text = language_manager.get_text(user_id, 'back_learning')
        back_main_text = language_manager.get_text(user_id, 'back_main')
        
        keyboard = [
            [InlineKeyboardButton(f"🔙 {back_to_learning_text}", callback_data="back_to_learning")],
            [InlineKeyboardButton(f"🏠 {back_main_text}", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """显示主菜单"""
        user = update.effective_user
        user_id = user.id
        
        welcome_text = language_manager.get_text(user_id, 'welcome', name=user.first_name)
        
        keyboard = [
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_reading'), callback_data="start_reading")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_daily'), callback_data="daily_card")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_learn'), callback_data="learn_tarot")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_language'), callback_data="language_select")],
            [InlineKeyboardButton(language_manager.get_text(user_id, 'menu_help'), callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """显示帮助信息"""
        user_id = update.effective_user.id
        help_text = language_manager.get_text(user_id, 'help_text')
        
        keyboard = [
            [InlineKeyboardButton(language_manager.get_text(user_id, 'back_main'), callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

def main():
    """启动机器人"""
    # 获取Bot Token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("请在.env文件中设置TELEGRAM_BOT_TOKEN")
        return
    
    # 创建机器人实例
    bot = TarotBot()
    
    # 创建应用
    application = Application.builder().token(token).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("daily", bot.daily_card_command))
    application.add_handler(CommandHandler("reading", bot.reading_command))
    application.add_handler(CommandHandler("learn", bot.learn_command))
    
    application.add_handler(CallbackQueryHandler(bot.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_question))
    
    # 启动机器人
    logger.info("塔罗预测机器人启动中...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()