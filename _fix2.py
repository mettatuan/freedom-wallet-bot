"""Fix show_main_menu callback to use get_main_keyboard()."""
with open('bot/handlers/webapp_setup.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 731-745 (0-indexed: 730-744)
# Replace the keyboard creation + old send_message with get_main_keyboard version
start = None
end = None
for i, line in enumerate(lines):
    if 'elif callback_data == "show_main_menu":' in line:
        start = i
    if start and i > start and '            await context.bot.send_message(' in line:
        # find the end of this send_message block
        for j in range(i, i + 10):
            if lines[j].strip() == ')':
                end = j + 1
                break
        break

if start is None or end is None:
    print(f'❌ Could not find block (start={start}, end={end})')
    exit(1)

print(f'Found show_main_menu block: lines {start+1}–{end}')
print('Old block:')
print(''.join(lines[start:end]))

new_block = '''        elif callback_data == "show_main_menu":
            await query.answer()
            from bot.core.keyboard import get_main_keyboard
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="📱 <b>MENU CHÍNH</b>\\n\\nDùng keyboard bên dưới để truy cập nhanh:",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
'''

lines[start:end] = [new_block]

with open('bot/handlers/webapp_setup.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Replaced show_main_menu callback with get_main_keyboard()')
