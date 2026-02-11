"""
Celebration Handler - Milestone celebrations vá»›i hÃ¬nh áº£nh cÃ¡ nhÃ¢n hÃ³a
Trao thÆ°á»Ÿng khi user Ä‘áº¡t Ä‘Æ°á»£c streak milestones
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
from app.utils.database import SessionLocal, User


def create_personalized_image(template_path: str, user_name: str, days: int, output_path: str) -> str:
    """
    Create personalized celebration image with user's name
    
    Args:
        template_path: Path to template image
        user_name: User's name to write on image
        days: Number of days (7, 30, 90...)
        output_path: Path to save personalized image
        
    Returns:
        Path to personalized image
    """
    try:
        # Open template image
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
        # Try to load custom font, fallback to default
        try:
            # Sá»­ dá»¥ng font Unicode support Vietnamese
            font_large = ImageFont.truetype("arial.ttf", 60)
            font_small = ImageFont.truetype("arial.ttf", 40)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Draw user name (centered, near top)
        name_text = user_name.upper()
        # Calculate text size using textbbox instead of deprecated textsize
        bbox = draw.textbbox((0, 0), name_text, font=font_large)
        name_width = bbox[2] - bbox[0]
        name_height = bbox[3] - bbox[1]
        
        name_x = (img_width - name_width) // 2
        name_y = int(img_height * 0.3)  # 30% from top
        
        # Draw text with outline for better visibility
        # Outline (black)
        outline_range = 3
        for adj_x in range(-outline_range, outline_range + 1):
            for adj_y in range(-outline_range, outline_range + 1):
                draw.text((name_x + adj_x, name_y + adj_y), name_text, font=font_large, fill="black")
        # Main text (white/gold)
        draw.text((name_x, name_y), name_text, font=font_large, fill="#FFD700")
        
        # Draw days (if milestone specific)
        if days > 0:
            days_text = f"{days} NGÃ€Y LIÃŠN Tá»¤C!"
            bbox_days = draw.textbbox((0, 0), days_text, font=font_small)
            days_width = bbox_days[2] - bbox_days[0]
            days_x = (img_width - days_width) // 2
            days_y = name_y + name_height + 20
            
            # Outline
            for adj_x in range(-2, 3):
                for adj_y in range(-2, 3):
                    draw.text((days_x + adj_x, days_y + adj_y), days_text, font=font_small, fill="black")
            # Main text
            draw.text((days_x, days_y), days_text, font=font_small, fill="white")
        
        # Save personalized image
        img.save(output_path)
        logger.info(f"Created personalized image: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating personalized image: {e}")
        # Return template if personalization fails
        return template_path


async def celebrate_7day_streak(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Celebrate 7-day streak with personalized image"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.milestone_7day_achieved:
            db.close()
            return
        
        # Get user name
        user_name = user.full_name or user.first_name or "Báº N"
        
        # Path to template and output
        template_path = "media/images/chuc_mung_7ngay.png"
        output_path = f"media/temp/celebration_7day_{user_id}.png"
        
        # Ensure temp directory exists
        os.makedirs("media/temp", exist_ok=True)
        
        # Create personalized image
        if os.path.exists(template_path):
            personalized_image = create_personalized_image(
                template_path=template_path,
                user_name=user_name,
                days=7,
                output_path=output_path
            )
        else:
            logger.warning(f"Template image not found: {template_path}")
            personalized_image = None
        
        # Celebration message
        message = f"""
ðŸŽ‰ **CHÃšC Má»ªNG {user_name.upper()}!**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ”¥ **Báº N ÄÃƒ GHI CHÃ‰P LIÃŠN Tá»¤C 7 NGÃ€Y!**

âœ¨ ÄÃ¢y lÃ  thÃ nh tÃ­ch tuyá»‡t vá»i! Chá»‰ cÃ³ **15% ngÆ°á»i dÃ¹ng** Ä‘áº¡t Ä‘Æ°á»£c má»‘c nÃ y!

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“Š **THá»NG KÃŠ Cá»¦A Báº N:**
â€¢ Tá»•ng giao dá»‹ch: {user.total_transactions or 0}
â€¢ Streak hiá»‡n táº¡i: 7 ngÃ y
â€¢ Streak dÃ i nháº¥t: {user.longest_streak or 7} ngÃ y

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ† **PHáº¦N THÆ¯á»žNG:**
â€¢ Badge "7-Day Champion"
â€¢ Unlock tÃ­nh nÄƒng Reports nÃ¢ng cao
â€¢ Æ¯u tiÃªn support trong Group VIP

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’ª **THÃCH THá»¨C TIáº¾P THEO:**
Äáº¡t 30 ngÃ y liÃªn tá»¥c Ä‘á»ƒ nháº­n:
â€¢ Huy chÆ°Æ¡ng danh dá»±
â€¢ ÄÆ°á»£c featured trÃªn Leaderboard
â€¢ QuÃ  táº·ng Ä‘áº·c biá»‡t tá»« Freedom Wallet

ðŸ”¥ **Tiáº¿p tá»¥c phÃ¡ ká»· lá»¥c thÃ´i!**
"""
        
        # Send celebration
        if personalized_image and os.path.exists(personalized_image):
            with open(personalized_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=message,
                    parse_mode="Markdown"
                )
            # Clean up temp file
            try:
                os.remove(personalized_image)
            except:
                pass
        else:
            # Send text only if image not available
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )
        
        # Mark milestone achieved
        user.milestone_7day_achieved = True
        db.commit()
        db.close()
        
        logger.info(f"Celebrated 7-day streak for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error celebrating 7-day streak for {user_id}: {e}")


async def celebrate_30day_streak(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Celebrate 30-day streak with medal and personalized image"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.milestone_30day_achieved:
            db.close()
            return
        
        # Get user name
        user_name = user.full_name or user.first_name or "Báº N"
        
        # Path to template and output
        template_path = "media/images/huy_chuong_30ngay.png"
        output_path = f"media/temp/celebration_30day_{user_id}.png"
        
        # Ensure temp directory exists
        os.makedirs("media/temp", exist_ok=True)
        
        # Create personalized image
        if os.path.exists(template_path):
            personalized_image = create_personalized_image(
                template_path=template_path,
                user_name=user_name,
                days=30,
                output_path=output_path
            )
        else:
            logger.warning(f"Template image not found: {template_path}")
            personalized_image = None
        
        # Celebration message
        message = f"""
ðŸ† **CHÃšC Má»ªNG {user_name.upper()}!**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ‘‘ **Báº N ÄÃƒ GHI CHÃ‰P LIÃŠN Tá»¤C 30 NGÃ€Y!**

âœ¨ ÄÃ¢y lÃ  thÃ nh tÃ­ch **XUáº¤T Sáº®C**! Chá»‰ cÃ³ **3% ngÆ°á»i dÃ¹ng** Ä‘áº¡t Ä‘Æ°á»£c!

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“Š **THá»NG KÃŠ Cá»¦A Báº N:**
â€¢ Tá»•ng giao dá»‹ch: {user.total_transactions or 0}
â€¢ Streak hiá»‡n táº¡i: 30 ngÃ y
â€¢ Streak dÃ i nháº¥t: {user.longest_streak or 30} ngÃ y
â€¢ Thá»i gian kiÃªn trÃ¬: 1 thÃ¡ng

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŽ–ï¸ **HUY CHÆ¯Æ NG DANH Dá»°:**
Báº¡n chÃ­nh thá»©c nháº­n:
â€¢ **Huy chÆ°Æ¡ng "30-Day Legend"**
â€¢ Featured trÃªn Leaderboard
â€¢ VIP Support Æ°u tiÃªn cao nháº¥t
â€¢ Exclusive access to Beta features
â€¢ QuÃ  táº·ng tá»« Freedom Wallet Team

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’Ž **Báº N ÄÃƒ HÃŒNH THÃ€NH THÃ“I QUEN:**
NghiÃªn cá»©u chá»‰ ra: 30 ngÃ y lÃ  Ä‘á»§ Ä‘á»ƒ táº¡o thÃ³i quen bá»n vá»¯ng!

BÃ¢y giá» quáº£n lÃ½ tÃ i chÃ­nh Ä‘Ã£ trá»Ÿ thÃ nh pháº§n tá»± nhiÃªn cá»§a cuá»™c sá»‘ng báº¡n! ðŸŽ¯

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸš€ **THÃCH THá»¨C TIáº¾P THEO:**
Äáº¡t 90 ngÃ y Ä‘á»ƒ trá»Ÿ thÃ nh **MASTER** vÃ  nháº­n:
â€¢ Chá»©ng nháº­n Master Certificate
â€¢ Exclusive merchandise
â€¢ CÆ¡ há»™i trá»Ÿ thÃ nh Ambassador

ðŸ’ª **Báº¡n Ä‘Ã£ lÃ m Ä‘Æ°á»£c rá»“i - Tiáº¿p tá»¥c chinh phá»¥c!**
"""
        
        # Send celebration
        if personalized_image and os.path.exists(personalized_image):
            with open(personalized_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=message,
                    parse_mode="Markdown"
                )
            # Clean up temp file
            try:
                os.remove(personalized_image)
            except:
                pass
        else:
            # Send text only if image not available
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )
        
        # Mark milestone achieved
        user.milestone_30day_achieved = True
        
        # Update user to SUPER_VIP if not already
        if user.user_state != "SUPER_VIP":
            user.user_state = "SUPER_VIP"
        
        db.commit()
        db.close()
        
        logger.info(f"Celebrated 30-day streak for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error celebrating 30-day streak for {user_id}: {e}")


async def celebrate_90day_streak(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Celebrate 90-day streak - MASTER level"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.milestone_90day_achieved:
            db.close()
            return
        
        # Get user name
        user_name = user.full_name or user.first_name or "Báº N"
        
        # Celebration message
        message = f"""
ðŸ‘‘ **{user_name.upper()} - Báº N LÃ€ HUYá»€N THOáº I!**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŒŸ **90 NGÃ€Y LIÃŠN Tá»¤C - MASTER LEVEL!**

âœ¨ Chá»‰ cÃ³ **1% ngÆ°á»i dÃ¹ng** Ä‘áº¡t Ä‘Æ°á»£c thÃ nh tÃ­ch nÃ y!

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“Š **Ká»¶ Lá»¤C Cá»¦A Báº N:**
â€¢ Tá»•ng giao dá»‹ch: {user.total_transactions or 0}
â€¢ Streak hiá»‡n táº¡i: 90 ngÃ y
â€¢ Thá»i gian kiÃªn trÃ¬: 3 thÃ¡ng
â€¢ Xáº¿p háº¡ng: **TOP 1%**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ… **MASTER CERTIFICATE:**
â€¢ Chá»©ng nháº­n Master Level
â€¢ Lifetime VIP Access
â€¢ Featured as Success Story
â€¢ Freedom Wallet merchandise
â€¢ Má»i tham gia Advisory Board

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’° **TÃC Äá»˜NG TÃ€I CHÃNH:**
Sau 90 ngÃ y, háº§u háº¿t users bÃ¡o cÃ¡o:
â€¢ Tiáº¿t kiá»‡m Ä‘Æ°á»£c 20-30% chi tiÃªu
â€¢ TÄƒng Ä‘áº§u tÆ° lÃªn 3-5x
â€¢ Giáº£m stress tÃ i chÃ­nh Ä‘Ã¡ng ká»ƒ
â€¢ Äáº¡t Ä‘Æ°á»£c Ã­t nháº¥t 1 má»¥c tiÃªu tÃ i chÃ­nh

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŽ¯ **Báº N ÄÃƒ THAY Äá»”I CUá»˜C Sá»NG:**
Quáº£n lÃ½ tÃ i chÃ­nh giá» lÃ  pháº§n khÃ´ng thá»ƒ thiáº¿u cá»§a báº¡n!

Cáº£m Æ¡n báº¡n Ä‘Ã£ tin tÆ°á»Ÿng Freedom Wallet! ðŸ™

ðŸ’Ž **Háº¹n gáº·p báº¡n á»Ÿ Ä‘á»‰nh cao tiáº¿p theo!**
"""
        
        # Send celebration
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown"
        )
        
        # Mark milestone achieved
        user.milestone_90day_achieved = True
        
        # Ensure SUPER_VIP status
        if user.user_state != "SUPER_VIP":
            user.user_state = "SUPER_VIP"
        
        db.commit()
        db.close()
        
        logger.info(f"Celebrated 90-day streak for user {user_id} - MASTER LEVEL!")
        
    except Exception as e:
        logger.error(f"Error celebrating 90-day streak for {user_id}: {e}")


def check_and_celebrate_milestone(user: User, context: ContextTypes.DEFAULT_TYPE):
    """
    Check if user reached a milestone and trigger celebration
    Called after user records a transaction
    """
    streak = user.streak_count
    
    # Check milestones
    if streak == 7 and not user.milestone_7day_achieved:
        # Schedule celebration
        context.application.create_task(
            celebrate_7day_streak(context, user.id)
        )
    
    elif streak == 30 and not user.milestone_30day_achieved:
        # Schedule celebration
        context.application.create_task(
            celebrate_30day_streak(context, user.id)
        )
    
    elif streak == 90 and not user.milestone_90day_achieved:
        # Schedule celebration
        context.application.create_task(
            celebrate_90day_streak(context, user.id)
        )

