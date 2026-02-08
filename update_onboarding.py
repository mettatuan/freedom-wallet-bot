# -*- coding: utf-8 -*-
"""Update onboarding message Day 1"""

# Read file
with open('bot/handlers/onboarding.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace Day 1 section (lines ~18-67)
new_lines = []
in_day1 = False
skip_until_buttons_end = False

for i, line in enumerate(lines):
    if '1: {' in line and i < 30:  # Start of Day 1
        in_day1 = True
        new_lines.append(line)
        # Add new title
        new_lines.append('        "title": "🎁 FREEDOM WALLET – BỘ KHỞI ĐỘNG & BƯỚC ĐẦU TIÊN",\n')
        new_lines.append('        "content": """\n')
        new_lines.append('👋 **Chào mừng bạn đến với Freedom Wallet!**\n')
        new_lines.append('\n')
        new_lines.append('Mình sẽ đồng hành cùng bạn trong 7 ngày tới để:\n')
        new_lines.append('• Thiết lập hệ thống quản lý tài chính cá nhân\n')
        new_lines.append('• Hiểu rõ 6 Hũ Tiền & 5 Cấp Bậc Tài Chính\n')
        new_lines.append('• Bắt đầu quản lý tiền một cách rõ ràng, hiệu quả\n')
        new_lines.append('\n')
        new_lines.append('🎯 Hôm nay, chúng ta chỉ cần làm **1 việc quan trọng nhất**.\n')
        new_lines.append('\n')
        new_lines.append('━━━━━━━━━━━━━━━━━━━━━\n')
        new_lines.append('\n')
        new_lines.append('🧭 **BƯỚC ĐẦU TIÊN – THIẾT LẬP FREEDOM WALLET**\n')
        new_lines.append('⏱ Thời gian: 10–15 phút (làm 1 lần duy nhất)\n')
        new_lines.append('\n')
        new_lines.append('Bạn sẽ:\n')
        new_lines.append('1️⃣ Copy Google Sheets Template\n')
        new_lines.append('2️⃣ Tạo Web App cá nhân (5 phút)\n')
        new_lines.append('3️⃣ Nhập dữ liệu đầu tiên (số dư + 1 giao dịch)\n')
        new_lines.append('\n')
        new_lines.append('👉 Không cần biết code.\n')
        new_lines.append('👉 Làm chậm cũng hoàn toàn ổn.\n')
        new_lines.append('\n')
        new_lines.append('━━━━━━━━━━━━━━━━━━━━━\n')
        new_lines.append('\n')
        new_lines.append('🎁 **BẠN ĐƯỢC CUNG CẤP ĐẦY ĐỦ CÔNG CỤ**\n')
        new_lines.append('\n')
        new_lines.append('📄 Template quản lý tài chính (Google Sheets)\n')
        new_lines.append('📚 Hướng dẫn Web App từng bước\n')
        new_lines.append('🎥 Video hướng dẫn nhanh (3 phút)\n')
        new_lines.append('💬 Cộng đồng hỗ trợ Freedom Wallet\n')
        new_lines.append('\n')
        new_lines.append('(Tất cả đã sẵn sàng – bạn chỉ cần bắt đầu)\n')
        new_lines.append('\n')
        new_lines.append('━━━━━━━━━━━━━━━━━━━━━\n')
        new_lines.append('\n')
        new_lines.append('💡 Hoàn thành bước này là bạn đã đi được **50% chặng đường**.\n')
        new_lines.append('""",\n')
        new_lines.append('        "delay_hours": 0,\n')
        new_lines.append('        "buttons": [\n')
        new_lines.append('            [{"text": "📑 Copy Template", "callback_data": "onboard_copy_template"}, \n')
        new_lines.append('             {"text": "🌐 Hướng dẫn Web App", "url": "https://eliroxbot.notion.site/freedomwallet"}],\n')
        new_lines.append('            [{"text": "✅ Hoàn thành bước đầu tiên", "callback_data": "onboard_complete_1"}, \n')
        new_lines.append('             {"text": "❓ Cần hỗ trợ", "callback_data": "onboard_help_1"}],\n')
        new_lines.append('            [{"text": "💬 Vào cộng đồng", "url": "https://t.me/freedomwalletapp"}, \n')
        new_lines.append('             {"text": "📋 Xem lộ trình 7 ngày", "callback_data": "onboard_roadmap"}]\n')
        new_lines.append('        ]\n')
        skip_until_buttons_end = True
        continue
    
    if skip_until_buttons_end:
        # Skip old Day 1 content until we hit the closing of buttons
        if '    },' in line and i < 70:  # End of Day 1 dict
            skip_until_buttons_end = False
            new_lines.append(line)
            in_day1 = False
        continue
    
    new_lines.append(line)

# Write back
with open('bot/handlers/onboarding.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✅ Successfully updated onboarding.py!')
print('📝 Changes:')
print('  - New title: FREEDOM WALLET – BỘ KHỞI ĐỘNG & BƯỚC ĐẦU TIÊN')
print('  - Condensed content (1 block vs 3 sections)')
print('  - New buttons: 6 buttons in 3 rows')
print('  - Added: "50% chặng đường" motivation')
