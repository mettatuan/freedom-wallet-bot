"""
🤖 FREEDOM WALLET BOT - CODE STRUCTURE
=====================================

Hybrid Architecture:
- Python: Telegram Bot Core, Business Logic, Database
- VBA/VB.NET: Excel/Google Sheets Automation, Report Generation
- Webhook: External integrations

Author: Freedom Wallet Team
Version: 2.0
"""

# ============================================================================
# PYTHON CORE - Telegram Bot Engine
# ============================================================================

# ----------------------------------------------------------------------------
# 1. STATE MACHINE HANDLER (Central Router)
# ----------------------------------------------------------------------------

class UserStateMachine:
    """
    Quản lý state transitions theo flowchart
    
    States:
    - VISITOR → REGISTERED → NURTURE_DAY_X → VIP → VIP_ACTIVATED 
      → VIP_GRADUATED → VIP_ENGAGED → SUPER_VIP_CANDIDATE → SUPER_VIP → ADVOCATE
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db = Database()
        self.current_state = self.db.get_user_state(user_id)
    
    def transition_to(self, new_state: str, context: dict = None):
        """
        State transition với validation và side effects
        
        Args:
            new_state: Target state
            context: Additional data for transition
        
        Returns:
            bool: Success status
        """
        # Validate transition
        if not self._is_valid_transition(self.current_state, new_state):
            logger.warning(f"Invalid transition: {self.current_state} → {new_state}")
            return False
        
        # Execute pre-transition hooks
        self._on_exit(self.current_state)
        
        # Update database
        self.db.update_user_state(self.user_id, new_state)
        
        # Execute post-transition hooks
        self._on_enter(new_state, context)
        
        self.current_state = new_state
        logger.info(f"User {self.user_id}: {self.current_state}")
        
        return True
    
    def _is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Kiểm tra transition hợp lệ theo state diagram"""
        
        valid_transitions = {
            'VISITOR': ['REGISTERED'],
            'REGISTERED': ['NURTURE_DAY_1', 'VIP'],
            'NURTURE_DAY_1': ['NURTURE_DAY_2', 'VIP'],
            'NURTURE_DAY_2': ['NURTURE_DAY_3', 'VIP'],
            # ... (mapping đầy đủ từ state diagram)
            'VIP': ['ONBOARDING_DAY_1', 'VIP_ACTIVATED'],
            'VIP_ENGAGED': ['SUPER_VIP_CANDIDATE'],
            'SUPER_VIP_CANDIDATE': ['SUPER_VIP'],
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    def _on_enter(self, state: str, context: dict = None):
        """Triggers khi vào state mới"""
        
        handlers = {
            'REGISTERED': self._handle_registered,
            'VIP': self._handle_vip_unlock,
            'SUPER_VIP': self._handle_super_vip_unlock,
            'VIP_GRADUATED': self._handle_graduation,
        }
        
        handler = handlers.get(state)
        if handler:
            handler(context)
    
    def _on_exit(self, state: str):
        """Cleanup khi rời khỏi state"""
        
        if state.startswith('NURTURE_DAY_'):
            # Cancel nurture campaign jobs
            self._cancel_nurture_jobs()
    
    # -------------------------------------------------------------------------
    # State-specific handlers
    # -------------------------------------------------------------------------
    
    def _handle_registered(self, context: dict):
        """User vừa đăng ký → Start nurture campaign"""
        from bot.handlers.daily_nurture import start_nurture_campaign
        start_nurture_campaign(self.user_id)
    
    def _handle_vip_unlock(self, context: dict):
        """User unlock VIP (2 refs) → Show gift menu + Super VIP challenge"""
        from bot.handlers.viral import show_super_vip_challenge
        show_super_vip_challenge(self.user_id)
    
    def _handle_super_vip_unlock(self, context: dict):
        """User unlock Super VIP (50 refs) → Enable revenue share"""
        from bot.handlers.viral import enable_revenue_sharing
        enable_revenue_sharing(self.user_id, rate=40.0)
    
    def _handle_graduation(self, context: dict):
        """User hoàn thành 7-day journey → Generate certificate"""
        from bot.handlers.education import generate_certificate
        
        quiz_score = self.db.get_quiz_score(self.user_id)
        generate_certificate(self.user_id, score=quiz_score)


# ----------------------------------------------------------------------------
# 2. VIRAL GROWTH MODULE
# ----------------------------------------------------------------------------

class ViralGrowthEngine:
    """
    Quản lý referral tracking, leaderboard, Super VIP challenges
    """
    
    def __init__(self):
        self.db = Database()
    
    async def process_referral(self, referrer_code: str, new_user_id: int) -> bool:
        """
        Xử lý referral mới
        
        Flow:
        1. Validate referrer code
        2. Create referral record
        3. Update referrer's counter
        4. Check milestone unlock (2 → VIP, 10 → Rising Star, 50 → Super VIP)
        5. Send notifications
        
        Returns:
            bool: Success status
        """
        # Find referrer
        referrer = self.db.find_user_by_referral_code(referrer_code)
        if not referrer:
            logger.error(f"Invalid referral code: {referrer_code}")
            return False
        
        # Create referral record
        self.db.create_referral(
            referrer_id=referrer.id,
            referred_id=new_user_id,
            source='telegram'  # Could track: telegram, zalo, facebook
        )
        
        # Update counter
        referrer.referral_count += 1
        self.db.save(referrer)
        
        # Check milestones
        await self._check_referral_milestones(referrer)
        
        return True
    
    async def _check_referral_milestones(self, user):
        """Kiểm tra và unlock milestones"""
        
        count = user.referral_count
        
        # Milestone: 2 refs → VIP
        if count == 2 and user.user_state == 'REGISTERED':
            await self._unlock_vip(user)
        
        # Milestone: 10 refs → Rising Star badge
        elif count == 10:
            await self._award_badge(user, 'rising_star')
            await self._send_milestone_message(user, 
                "🌟 RISING STAR!\n\n"
                "10 giới thiệu thành công!\n"
                "Còn 40 nữa để đạt Super VIP 🚀"
            )
        
        # Milestone: 50 refs → Super VIP
        elif count == 50:
            await self._unlock_super_vip(user)
    
    async def _unlock_vip(self, user):
        """Unlock VIP tier"""
        
        # Update state
        state_machine = UserStateMachine(user.id)
        state_machine.transition_to('VIP')
        
        # Send congratulation image
        from pathlib import Path
        image_path = Path("media/images/chucmung.png")
        
        await bot.send_photo(
            chat_id=user.telegram_id,
            photo=image_path,
            caption=(
                "🎉 CHÚC MỪNG!\n\n"
                "Bạn đã hoàn thành 2/2 lượt giới thiệu!\n"
                "VIP UNLOCKED 💎"
            )
        )
        
        # Show Super VIP challenge
        await self._show_super_vip_challenge(user)
    
    async def _show_super_vip_challenge(self, user):
        """Hiển thị Super VIP challenge với counter"""
        
        # Get slots remaining
        config = self.db.get_super_vip_config()
        slots_remaining = config.total_slots - config.slots_filled
        
        if slots_remaining <= 0:
            # No more slots
            message = (
                "🎁 **MENU NHẬN QUÀ VIP**\n\n"
                "Chọn quà của bạn bên dưới..."
            )
        else:
            # Show challenge
            message = (
                f"💎 **THÁCH THỨC SUPER VIP**\n\n"
                f"Giới thiệu thêm 48 bạn (50 - 2 hiện tại)\n"
                f"→ Nhận 40% doanh thu từ người được giới thiệu\n\n"
                f"⏰ Còn **{slots_remaining}/100** suất\n\n"
                f"🏆 **TOP 10 HIỆN TẠI:**\n"
            )
            
            # Add leaderboard
            top_10 = self.db.get_top_referrers(limit=10)
            for i, ref in enumerate(top_10, 1):
                badge = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "▪️"
                message += f"{badge} {ref.full_name}: {ref.referral_count} refs\n"
        
        keyboard = [
            [InlineKeyboardButton("🔥 Tiếp tục chia sẻ", callback_data="share_link")],
            [InlineKeyboardButton("🎁 Nhận quà VIP", callback_data="vip_gifts")],
            [InlineKeyboardButton("🏠 Vào Dashboard", callback_data="start")]
        ]
        
        await bot.send_message(
            chat_id=user.telegram_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    async def _unlock_super_vip(self, user):
        """Unlock Super VIP tier"""
        
        # Check slots available
        config = self.db.get_super_vip_config()
        if config.slots_filled >= config.total_slots:
            await bot.send_message(
                chat_id=user.telegram_id,
                text="😢 Rất tiếc! Super VIP slots đã hết."
            )
            return
        
        # Update state
        state_machine = UserStateMachine(user.id)
        state_machine.transition_to('SUPER_VIP')
        
        # Update config
        config.slots_filled += 1
        self.db.save(config)
        
        # Enable revenue sharing
        user.revenue_share_enabled = True
        user.revenue_share_rate = 40.0
        self.db.save(user)
        
        # Send congratulation
        await bot.send_message(
            chat_id=user.telegram_id,
            text=(
                "🏆 **SUPER VIP UNLOCKED!**\n\n"
                "Chúc mừng! Bạn là 1 trong 100 Super VIP đầu tiên!\n\n"
                "💰 **Phần thưởng:**\n"
                "• 40% doanh thu từ 50+ người giới thiệu\n"
                "• Công cụ Coach độc quyền\n"
                "• Super VIP Group\n\n"
                "📧 Team sẽ liên hệ setup trong 24h."
            ),
            parse_mode="Markdown"
        )


# ----------------------------------------------------------------------------
# 3. EDUCATION MODULE (Quiz System)
# ----------------------------------------------------------------------------

class QuizEngine:
    """
    Quản lý quiz, scoring, certificates
    """
    
    def __init__(self):
        self.db = Database()
    
    async def send_quiz(self, user_id: int, day: int):
        """
        Gửi quiz cho user
        
        Args:
            user_id: User ID
            day: Onboarding day (1-7)
        """
        # Get quiz from content library
        quiz = self.db.get_quiz_for_day(day)
        
        if not quiz:
            logger.error(f"No quiz found for day {day}")
            return
        
        # Create inline keyboard với options
        keyboard = []
        for option_key, option_text in quiz.options.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{option_key}) {option_text}",
                    callback_data=f"quiz_{day}_{option_key}"
                )
            ])
        
        message = (
            f"📝 **MINI QUIZ - Ngày {day}**\n\n"
            f"{quiz.question_text}\n\n"
            f"Chọn đáp án đúng nhất:"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    async def process_quiz_answer(
        self, 
        user_id: int, 
        day: int, 
        answer: str
    ) -> dict:
        """
        Xử lý câu trả lời quiz
        
        Returns:
            dict: {
                'is_correct': bool,
                'points_awarded': int,
                'explanation': str,
                'can_retry': bool
            }
        """
        # Get quiz
        quiz = self.db.get_quiz_for_day(day)
        
        # Check answer
        is_correct = (answer == quiz.correct_answer)
        
        # Count previous attempts
        attempts = self.db.count_quiz_attempts(user_id, day)
        
        # Award points (only first correct answer)
        points = 10 if is_correct and attempts == 0 else 0
        
        # Save attempt
        self.db.create_quiz_attempt(
            user_id=user_id,
            quiz_day=day,
            user_answer=answer,
            correct_answer=quiz.correct_answer,
            is_correct=is_correct,
            points_awarded=points,
            attempt_number=attempts + 1
        )
        
        # Update user score
        if points > 0:
            user = self.db.get_user(user_id)
            user.quiz_score += points
            self.db.save(user)
        
        return {
            'is_correct': is_correct,
            'points_awarded': points,
            'explanation': quiz.explanation,
            'can_retry': attempts < 2  # Max 3 attempts
        }
    
    async def generate_certificate(self, user_id: int):
        """
        Tạo certificate image (shareable)
        
        Uses:
        - PIL (Python Imaging Library) to generate image
        - Or call VBA macro to generate from Excel template
        """
        user = self.db.get_user(user_id)
        
        # Option 1: Python PIL
        from PIL import Image, ImageDraw, ImageFont
        
        template = Image.open("media/templates/certificate_template.png")
        draw = ImageDraw.Draw(template)
        
        font_name = ImageFont.truetype("arial.ttf", 48)
        font_score = ImageFont.truetype("arial.ttf", 64)
        
        # Draw user name
        draw.text((400, 300), user.full_name, font=font_name, fill=(0, 0, 0))
        
        # Draw score
        draw.text((400, 400), f"{user.quiz_score}/70", font=font_score, fill=(255, 0, 0))
        
        # Save
        output_path = f"data/certificates/{user_id}.png"
        template.save(output_path)
        
        # Send to user
        await bot.send_photo(
            chat_id=user.telegram_id,
            photo=open(output_path, 'rb'),
            caption=(
                "🎓 **CHỨNG NHẬN HOÀN THÀNH**\n\n"
                f"Điểm số: {user.quiz_score}/70\n\n"
                "Chia sẻ thành tích của bạn! 📤"
            )
        )
        
        # Mark issued
        user.certificate_issued = True
        self.db.save(user)
        
        # Option 2: Call VBA macro (see VBA section below)
        # vba_engine.generate_certificate(user_id, user.full_name, user.quiz_score)


# ----------------------------------------------------------------------------
# 4. ACTIVATION MODULE (Checklist)
# ----------------------------------------------------------------------------

class ActivationEngine:
    """
    Quản lý activation checklist
    """
    
    TASKS = [
        {'id': 'task_1', 'name': 'Copy template về máy'},
        {'id': 'task_2', 'name': 'Thêm thu nhập đầu tiên'},
        {'id': 'task_3', 'name': 'Thêm chi tiêu đầu tiên'},
        {'id': 'task_4', 'name': 'Xem 6 Hũ auto tính'},
        {'id': 'task_5', 'name': 'Deploy Web App'},
    ]
    
    def __init__(self):
        self.db = Database()
    
    async def send_checklist(self, user_id: int):
        """Gửi activation checklist"""
        
        # Initialize tasks
        for task in self.TASKS:
            self.db.create_activation_task(
                user_id=user_id,
                task_id=task['id'],
                task_name=task['name']
            )
        
        message = self._build_checklist_message(user_id)
        keyboard = self._build_checklist_keyboard(user_id)
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    def _build_checklist_message(self, user_id: int) -> str:
        """Build checklist message với progress"""
        
        tasks = self.db.get_activation_tasks(user_id)
        completed = sum(1 for t in tasks if t.status == 'COMPLETED')
        
        message = (
            "🎯 **NHIỆM VỤ KÍCH HOẠT**\n\n"
            f"Tiến độ: {completed}/{len(self.TASKS)}\n\n"
        )
        
        for task in tasks:
            status_icon = "✅" if task.status == 'COMPLETED' else "☐"
            message += f"{status_icon} {task.task_name}\n"
        
        message += "\n📸 Hoàn thành để nhận badge **First Success** 🏆"
        
        return message
    
    def _build_checklist_keyboard(self, user_id: int):
        """Build inline keyboard cho tasks"""
        
        tasks = self.db.get_activation_tasks(user_id)
        keyboard = []
        
        for task in tasks:
            if task.status != 'COMPLETED':
                keyboard.append([
                    InlineKeyboardButton(
                        f"📖 {task.task_name}",
                        callback_data=f"checklist_{task.task_id}"
                    )
                ])
        
        keyboard.append([
            InlineKeyboardButton("✅ Đánh dấu hoàn thành", callback_data="checklist_complete")
        ])
        
        return keyboard
    
    async def complete_task(self, user_id: int, task_id: str):
        """Mark task as completed"""
        
        task = self.db.get_activation_task(user_id, task_id)
        task.status = 'COMPLETED'
        task.completed_at = datetime.now()
        self.db.save(task)
        
        # Check if all tasks completed
        all_tasks = self.db.get_activation_tasks(user_id)
        all_completed = all(t.status == 'COMPLETED' for t in all_tasks)
        
        if all_completed:
            await self._handle_activation_complete(user_id)
        else:
            # Update progress
            await self.send_checklist(user_id)
    
    async def _handle_activation_complete(self, user_id: int):
        """User hoàn thành tất cả tasks"""
        
        # Update user state
        user = self.db.get_user(user_id)
        user.activation_status = 'COMPLETED'
        self.db.save(user)
        
        # Award badge
        viral_engine = ViralGrowthEngine()
        await viral_engine._award_badge(user, 'first_success')
        
        # Send congratulation
        await bot.send_message(
            chat_id=user.telegram_id,
            text=(
                "🎉 **ACTIVATION HOÀN THÀNH!**\n\n"
                "Bạn đã hoàn thành 5/5 nhiệm vụ kích hoạt!\n\n"
                "🏆 Badge: **First Success**\n\n"
                "Tiếp tục hành trình 7 ngày để master Freedom Wallet! 🚀"
            ),
            parse_mode="Markdown"
        )


# ----------------------------------------------------------------------------
# 5. RETENTION MODULE (Weekly Review)
# ----------------------------------------------------------------------------

class RetentionEngine:
    """
    Quản lý weekly reports, re-engagement
    """
    
    def __init__(self):
        self.db = Database()
        self.vba_engine = VBAEngine()  # For Excel report generation
    
    async def generate_weekly_report(self, user_id: int):
        """
        Tạo weekly report
        
        Flow:
        1. Fetch user's Google Sheet data (via VBA or Sheets API)
        2. Calculate metrics
        3. Compare vs last week
        4. Generate personalized message
        5. Send report
        """
        user = self.db.get_user(user_id)
        
        # Fetch data from user's Google Sheet
        sheet_data = await self._fetch_user_sheet_data(user)
        
        if not sheet_data:
            # User inactive
            await self._send_reengagement_message(user)
            return
        
        # Calculate metrics
        metrics = self._calculate_metrics(sheet_data)
        
        # Get last week's report for comparison
        last_week = self.db.get_last_weekly_report(user_id)
        
        # Compare
        income_change = self._calculate_change(
            metrics['total_income'],
            last_week.total_income if last_week else 0
        )
        
        expense_change = self._calculate_change(
            metrics['total_expense'],
            last_week.total_expense if last_week else 0
        )
        
        # Save report
        self.db.create_weekly_report(
            user_id=user_id,
            week_start=metrics['week_start'],
            week_end=metrics['week_end'],
            total_income=metrics['total_income'],
            total_expense=metrics['total_expense'],
            income_vs_last_week=income_change,
            expense_vs_last_week=expense_change,
            **metrics['jars']
        )
        
        # Generate message
        message = self._build_weekly_message(user, metrics, income_change, expense_change)
        
        # Send
        await bot.send_message(
            chat_id=user.telegram_id,
            text=message,
            reply_markup=self._build_weekly_keyboard(),
            parse_mode="Markdown"
        )
    
    async def _fetch_user_sheet_data(self, user) -> dict:
        """
        Fetch data từ Google Sheet của user
        
        Option 1: Python gspread
        Option 2: Call VBA macro to read Excel
        """
        # Option 1: Python gspread (if user shared sheet with bot)
        try:
            from bot.utils.sheets import get_sheets_client
            
            client = get_sheets_client()
            sheet = client.open_by_url(user.sheet_url)
            worksheet = sheet.worksheet("Dashboard")
            
            data = {
                'total_income': worksheet.acell('B5').value,
                'total_expense': worksheet.acell('B6').value,
                # ... read more cells
            }
            
            return data
        
        except Exception as e:
            logger.error(f"Failed to fetch sheet data: {e}")
            return None
    
    def _build_weekly_message(self, user, metrics, income_change, expense_change):
        """Build personalized weekly message"""
        
        # Determine trend
        if income_change > 0 and expense_change < 0:
            trend_message = "🎉 Xuất sắc! Thu tăng, chi giảm!"
        elif income_change < 0 and expense_change > 0:
            trend_message = "⚠️ Cần điều chỉnh. Thu giảm, chi tăng."
        else:
            trend_message = "📊 Ổn định. Tiếp tục duy trì!"
        
        # Personalized tip based on segment
        segment = user.user_segment
        if segment == 'STUDENT':
            tip = "💡 **Tip**: Tối ưu hũ PLAY bằng cách tìm hoạt động giải trí miễn phí."
        elif segment == 'WORKING':
            tip = "💡 **Tip**: Tăng hũ LTS lên 12-15% để đạt tự do tài chính sớm hơn."
        else:  # INVESTOR
            tip = "💡 **Tip**: Đa dạng hóa hũ FFA với các kênh đầu tư rủi ro thấp."
        
        message = (
            f"📈 **BÁO CÁO TUẦN {metrics['week_start']} - {metrics['week_end']}**\n\n"
            f"{trend_message}\n\n"
            f"💰 **Thu nhập**: {metrics['total_income']:,.0f} đ ({income_change:+.1f}%)\n"
            f"💸 **Chi tiêu**: {metrics['total_expense']:,.0f} đ ({expense_change:+.1f}%)\n"
            f"💵 **Net cashflow**: {metrics['net_cashflow']:,.0f} đ\n\n"
            f"🏺 **6 Hũ Tiền:**\n"
            f"  • NEC: {metrics['jars']['jar_nec']:,.0f} đ\n"
            f"  • LTS: {metrics['jars']['jar_lts']:,.0f} đ\n"
            f"  • EDU: {metrics['jars']['jar_edu']:,.0f} đ\n"
            f"  • PLAY: {metrics['jars']['jar_play']:,.0f} đ\n"
            f"  • FFA: {metrics['jars']['jar_ffa']:,.0f} đ\n"
            f"  • GIVE: {metrics['jars']['jar_give']:,.0f} đ\n\n"
            f"{tip}"
        )
        
        return message


# ============================================================================
# VISUAL BASIC - Excel / Google Sheets Automation
# ============================================================================

"""
VBA CODE STRUCTURE (Excel Macros)
==================================

Đoạn VB này chạy trong Excel/Google Sheets Apps Script
để automation các tác vụ:
- Generate certificate từ template
- Fetch user data từ sheet
- Generate report charts
- Export PDF/Image

"""

VBA_CODE = '''
' ============================================================================
' Module 1: CertificateGenerator
' ============================================================================

Option Explicit

Sub GenerateCertificate(userName As String, quizScore As Integer)
    '''
    ' Tạo certificate từ template Excel
    ' 
    ' Args:
    '   userName: Tên user
    '   quizScore: Điểm quiz (0-70)
    '''
    
    Dim ws As Worksheet
    Dim certPath As String
    
    ' Mở template
    Set ws = ThisWorkbook.Worksheets("CertificateTemplate")
    
    ' Fill data
    ws.Range("B5").Value = userName
    ws.Range("B6").Value = quizScore & "/70"
    ws.Range("B7").Value = Format(Date, "dd/mm/yyyy")
    
    ' Export as image
    certPath = "C:\\Certificates\\" & userName & ".png"
    Call ExportRangeAsImage(ws.Range("A1:K20"), certPath)
    
    ' Send to bot via webhook
    Call SendToTelegramBot(certPath, userName)
    
    MsgBox "Certificate generated: " & certPath
End Sub

Sub ExportRangeAsImage(rng As Range, filePath As String)
    '''
    ' Export Excel range as PNG image
    '''
    
    Dim cht As Chart
    
    ' Copy range as image
    rng.CopyPicture Appearance:=xlScreen, Format:=xlPicture
    
    ' Create temp chart
    Set cht = Charts.Add
    With cht
        .Paste
        .Export filePath, "PNG"
    End With
    
    cht.Delete
End Sub

' ============================================================================
' Module 2: UserDataFetcher
' ============================================================================

Sub FetchUserWeeklyData(userId As Long) As Dictionary
    '''
    ' Đọc data từ Google Sheet của user
    ' 
    ' Returns:
    '   Dictionary với keys: total_income, total_expense, jars, etc.
    '''
    
    Dim ws As Worksheet
    Dim data As New Dictionary
    
    ' Giả sử mỗi user có 1 sheet riêng
    Set ws = ThisWorkbook.Worksheets("User_" & userId)
    
    ' Read dashboard metrics
    data.Add "total_income", ws.Range("Dashboard!B5").Value
    data.Add "total_expense", ws.Range("Dashboard!B6").Value
    data.Add "net_cashflow", ws.Range("Dashboard!B7").Value
    
    ' Read jars
    data.Add "jar_nec", ws.Range("Dashboard!B10").Value
    data.Add "jar_lts", ws.Range("Dashboard!B11").Value
    data.Add "jar_edu", ws.Range("Dashboard!B12").Value
    data.Add "jar_play", ws.Range("Dashboard!B13").Value
    data.Add "jar_ffa", ws.Range("Dashboard!B14").Value
    data.Add "jar_give", ws.Range("Dashboard!B15").Value
    
    ' Count transactions
    Dim lastRow As Long
    lastRow = ws.Range("Transactions!A" & ws.Rows.Count).End(xlUp).Row
    data.Add "transaction_count", lastRow - 1  ' Minus header
    
    Set FetchUserWeeklyData = data
End Sub

' ============================================================================
' Module 3: ReportGenerator
' ============================================================================

Sub GenerateWeeklyReport(userId As Long)
    '''
    ' Tạo weekly report chart và export
    '''
    
    Dim ws As Worksheet
    Dim cht As Chart
    
    Set ws = ThisWorkbook.Worksheets("User_" & userId)
    
    ' Create chart
    Set cht = ws.Shapes.AddChart2.Chart
    With cht
        .ChartType = xlColumnClustered
        .SetSourceData Source:=ws.Range("Dashboard!A10:B15")
        .HasTitle = True
        .ChartTitle.Text = "6 Jars Balance"
    End With
    
    ' Export chart
    Dim chartPath As String
    chartPath = "C:\\Reports\\User_" & userId & "_weekly.png"
    cht.Export chartPath, "PNG"
    
    ' Send to bot
    Call SendToTelegramBot(chartPath, "weekly_report")
End Sub

' ============================================================================
' Module 4: TelegramWebhook
' ============================================================================

Sub SendToTelegramBot(filePath As String, dataType As String)
    '''
    ' Gửi file đến Telegram bot via webhook
    '''
    
    Dim http As Object
    Dim url As String
    Dim boundary As String
    Dim postData As String
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Webhook URL (Python bot endpoint)
    url = "http://localhost:5000/webhook/excel"
    
    ' Build multipart form data
    boundary = "----VBFormBoundary" & Format(Now, "yyyymmddhhnnss")
    
    postData = "--" & boundary & vbCrLf
    postData = postData & "Content-Disposition: form-data; name=""type""" & vbCrLf & vbCrLf
    postData = postData & dataType & vbCrLf
    postData = postData & "--" & boundary & vbCrLf
    postData = postData & "Content-Disposition: form-data; name=""file""; filename=""" & Dir(filePath) & """" & vbCrLf
    postData = postData & "Content-Type: image/png" & vbCrLf & vbCrLf
    postData = postData & ReadBinaryFile(filePath) & vbCrLf
    postData = postData & "--" & boundary & "--"
    
    ' Send POST request
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "multipart/form-data; boundary=" & boundary
    http.send postData
    
    ' Check response
    If http.Status = 200 Then
        Debug.Print "Sent to bot successfully"
    Else
        Debug.Print "Error: " & http.Status
    End If
End Sub

Function ReadBinaryFile(filePath As String) As String
    '''
    ' Đọc binary file cho multipart upload
    '''
    
    Dim stream As Object
    Set stream = CreateObject("ADODB.Stream")
    
    stream.Type = 1  ' Binary
    stream.Open
    stream.LoadFromFile filePath
    
    ReadBinaryFile = stream.Read
    stream.Close
End Function
'''

# ============================================================================
# WEBHOOK ENDPOINT (Python Flask) - Nhận data từ VBA
# ============================================================================

from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/excel', methods=['POST'])
def handle_excel_webhook():
    """
    Nhận file từ VBA Excel
    
    Expected form data:
    - type: 'certificate' | 'weekly_report'
    - file: binary image file
    """
    
    data_type = request.form.get('type')
    file = request.files.get('file')
    
    if not file:
        return {'error': 'No file provided'}, 400
    
    # Save file
    file_path = f"data/uploads/{file.filename}"
    file.save(file_path)
    
    # Process based on type
    if data_type == 'certificate':
        # Extract user info from filename
        user_name = file.filename.replace('.png', '')
        user = db.find_user_by_name(user_name)
        
        # Send certificate via bot
        bot.send_photo(
            chat_id=user.telegram_id,
            photo=open(file_path, 'rb'),
            caption="🎓 Certificate của bạn đây!"
        )
    
    elif data_type == 'weekly_report':
        # Similar processing for weekly report
        pass
    
    return {'status': 'success'}, 200


# ============================================================================
# CRON JOBS - Scheduled tasks
# ============================================================================

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Monday 9AM - Weekly reports
scheduler.add_job(
    send_all_weekly_reports,
    'cron',
    day_of_week='mon',
    hour=9,
    minute=0
)

# Thursday 9AM - Second weekly content
scheduler.add_job(
    send_weekly_tips,
    'cron',
    day_of_week='thu',
    hour=9,
    minute=0
)

scheduler.start()


async def send_all_weekly_reports():
    """Gửi weekly report cho tất cả VIP users"""
    
    retention = RetentionEngine()
    vip_users = db.get_all_vip_users()
    
    for user in vip_users:
        try:
            await retention.generate_weekly_report(user.id)
        except Exception as e:
            logger.error(f"Failed to send report to {user.id}: {e}")


async def send_weekly_tips():
    """Gửi tips vào thứ 5"""
    
    # Similar logic
    pass
