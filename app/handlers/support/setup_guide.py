"""
Setup Guide Handler - Step-by-step usage guide
Structure: Setup (3 steps) â†’ Accounts â†’ Categories â†’ Debts â†’ Investments â†’ Assets
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from loguru import logger

# Setup Guide Content - 10 Steps (New structure)
SETUP_GUIDE_STEPS = {
    0: {
        "title": "ðŸ“˜ BÆ¯á»šC 2: HÆ¯á»šNG DáºªN Sá»¬ Dá»¤NG",
        "content": """
ðŸŽ‰ **Tuyá»‡t vá»i! Báº¡n Ä‘Ã£ hoÃ n thÃ nh BÆ°á»›c 1!**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“ Báº N ÄANG á»ž ÄÃ‚U?**

âœ… BÆ°á»›c 1: Táº¡o Web App (hoÃ n thÃ nh)
âž¡ï¸ **BÆ¯á»šC 2: Há»c cÃ¡ch sá»­ dá»¥ng** (báº¡n Ä‘ang á»Ÿ Ä‘Ã¢y)

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸŽ¯ CÃCH Sá»¬ Dá»¤NG HIá»†U QUáº¢**

**1ï¸âƒ£ CÃ€I Äáº¶T** (3 bÆ°á»›c)
   a. XÃ³a dá»¯ liá»‡u máº«u
   b. CÃ i Ä‘áº·t hÅ© tiá»n
   c. 5 Cáº¥p báº­c tÃ i chÃ­nh

**2ï¸âƒ£ TÃ€I KHOáº¢N** - Biáº¿t tiá»n á»Ÿ Ä‘Ã¢u

**3ï¸âƒ£ DANH Má»¤C** - PhÃ¢n loáº¡i chi tiÃªu

**4ï¸âƒ£ KHOáº¢N Ná»¢** - LÃ m chá»§ ná»£

**5ï¸âƒ£ Äáº¦U TÆ¯** - Tiá»n lÃ m viá»‡c cho báº¡n

**6ï¸âƒ£ TÃ€I Sáº¢N** - TÃ­nh Net Worth

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

â± **Thá»i gian**: 15-20 phÃºt
ðŸ’¡ *Xem láº¡i: /huongdan*
""",
        "image": None
    },
    
    1: {
        "title": "âš™ï¸ CÃ€I Äáº¶T (1/3) â€“ XÃ“A Dá»® LIá»†U MáºªU",
        "content": """
**ðŸŽ¯ Má»¥c tiÃªu: LÃ m sáº¡ch app, chuáº©n bá»‹ nháº­p dá»¯ liá»‡u tháº­t**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“‹ CÃCH LÃ€M:**

1ï¸âƒ£ Má»Ÿ Web App cá»§a báº¡n

2ï¸âƒ£ VÃ o **CÃ i Ä‘áº·t** (Settings) á»Ÿ menu trÃªn

3ï¸âƒ£ Nháº¥n **XÃ³a dá»¯ liá»‡u máº«u** (Delete Sample Data)

4ï¸âƒ£ XÃ¡c nháº­n â†’ Táº¥t cáº£ dá»¯ liá»‡u máº«u bá»‹ xÃ³a

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**âœ… Káº¾T QUáº¢:**
â€¢ App "tráº¯ng tinh"
â€¢ Sáºµn sÃ ng cho dá»¯ liá»‡u thá»±c táº¿

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ’¡ LÆ°u Ã½:**
*Chá»‰ xÃ³a dá»¯ liá»‡u máº«u 1 láº§n duy nháº¥t khi báº¯t Ä‘áº§u!*
""",
        "image": "media/images/cai_dat.png"
    },
    
    2: {
        "title": "âš™ï¸ CÃ€I Äáº¶T (2/3) â€“ CÃ€I Äáº¶T HÅ¨ TIá»€N",
        "content": """
**ðŸŽ¯ Má»¥c tiÃªu: Thiáº¿t láº­p 6 HÅ© Tiá»n - TrÃ¡i tim Freedom Wallet**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸŽ¯ 6 HÅ¨ TIÃŠU CHUáº¨N:**

1ï¸âƒ£ **ðŸ  Chi tiÃªu thiáº¿t yáº¿u** (55%)
2ï¸âƒ£ **ðŸŽ‰ HÆ°á»Ÿng thá»¥** (10%)
3ï¸âƒ£ **ðŸŽ“ GiÃ¡o dá»¥c** (10%)
4ï¸âƒ£ **ðŸ’° Tiáº¿t kiá»‡m dÃ i háº¡n** (10%)
5ï¸âƒ£ **ðŸ’¼ Äáº§u tÆ°** (10%)
6ï¸âƒ£ **â¤ï¸ Cho Ä‘i** (5%)

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“‹ CÃCH LÃ€M:**

1ï¸âƒ£ VÃ o **CÃ i Ä‘áº·t** â†’ **6 Jars Settings**

2ï¸âƒ£ Nháº­p % cho tá»«ng hÅ© (tá»•ng = 100%)

3ï¸âƒ£ LÆ°u láº¡i â†’ Há»‡ thá»‘ng tá»± Ä‘á»™ng phÃ¢n bá»•

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**âœ… Káº¾T QUáº¢:**
â€¢ Má»—i khoáº£n thu tá»± Ä‘á»™ng phÃ¢n bá»•
â€¢ TiÃªu tiá»n cÃ³ ká»‰ luáº­t
â€¢ Vá»«a sá»‘ng tá»‘t, vá»«a giÃ u lÃªn
""",
        "image": "media/images/hu_tien.jpg"
    },
    
    3: {
        "title": "âš™ï¸ CÃ€I Äáº¶T (3/3) â€“ 5 Cáº¤P Báº¬C TÃ€I CHÃNH",
        "content": """
**ðŸŽ¯ Má»¥c tiÃªu: XÃ¡c Ä‘á»‹nh báº¡n Ä‘ang á»Ÿ Ä‘Ã¢u, Ä‘i Ä‘áº¿n Ä‘Ã¢u**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“ˆ 5 Cáº¤P Báº¬C:**

ðŸ”´ **Cáº¥p 1: BÃ¬nh á»•n tÃ i chÃ­nh**
   â†’ Chi tiÃªu báº±ng thu nháº­p

ðŸŸ  **Cáº¥p 2: An toÃ n tÃ i chÃ­nh**
   â†’ CÃ³ quá»¹ dá»± phÃ²ng 3-6 thÃ¡ng

ðŸŸ¡ **Cáº¥p 3: Äá»™c láº­p tÃ i chÃ­nh**
   â†’ KhÃ´ng phá»¥ thuá»™c lÆ°Æ¡ng

ðŸŸ¢ **Cáº¥p 4: Tá»± do tÃ i chÃ­nh**
   â†’ Thu nháº­p thá»¥ Ä‘á»™ng > chi tiÃªu

ðŸ”µ **Cáº¥p 5: Dá»“i dÃ o tÃ i chÃ­nh**
   â†’ LÃ m Ä‘Æ°á»£c báº¥t cá»© Ä‘iá»u gÃ¬

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“‹ CÃCH DÃ™NG:**

1ï¸âƒ£ Tá»± Ä‘Ã¡nh giÃ¡ báº¡n Ä‘ang á»Ÿ cáº¥p nÃ o

2ï¸âƒ£ Äáº·t má»¥c tiÃªu lÃªn cáº¥p tiáº¿p theo

3ï¸âƒ£ Theo dÃµi tiáº¿n Ä‘á»™ hÃ ng thÃ¡ng

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**âœ… Káº¾T QUáº¢:**
â€¢ CÃ³ lá»™ trÃ¬nh rÃµ rÃ ng
â€¢ Äá»™ng lá»±c thÃºc Ä‘áº©y
â€¢ Biáº¿t mÃ¬nh cáº§n lÃ m gÃ¬
""",
        "image": "media/images/5_cap_bac_tai_chinh.jpg"
    },
    
    4: {
        "title": "ðŸ’³ TÃ€I KHOáº¢N â€“ BIáº¾T TIá»€N á»ž ÄÃ‚U",
        "content": """
**ðŸŽ¯ Má»¥c tiÃªu: Biáº¿t tiá»n cá»§a báº¡n Ä‘ang náº±m á»Ÿ Ä‘Ã¢u**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“Œ VÃ Dá»¤ TÃ€I KHOáº¢N:**

â€¢ ðŸ’µ Tiá»n máº·t
â€¢ ðŸ¦ TÃ i khoáº£n ngÃ¢n hÃ ng (VCB, TCB, MB...)
â€¢ ðŸ“± VÃ­ Ä‘iá»‡n tá»­ (Momo, ZaloPay, VNPay...)

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“‹ CÃCH LÃ€M:**

1ï¸âƒ£ VÃ o má»¥c **Accounts** (TÃ i khoáº£n)

2ï¸âƒ£ âž• ThÃªm táº¥t cáº£ tÃ i khoáº£n cá»§a báº¡n

3ï¸âƒ£ Nháº­p **sá»‘ dÆ° ban Ä‘áº§u** (pháº£i khá»›p vá»›i thá»±c táº¿!)

4ï¸âƒ£ LÆ°u láº¡i â†’ Xem tá»•ng tÃ i sáº£n

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**âœ… Káº¾T QUáº¢:**
â€¢ Biáº¿t tá»•ng tiá»n cÃ³ bao nhiÃªu
â€¢ Tiá»n náº±m á»Ÿ Ä‘Ã¢u
â€¢ Ná»n táº£ng cho tracking sau nÃ y

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ’¡ Quan trá»ng:**
*Sá»‘ dÆ° ban Ä‘áº§u sai â†’ táº¥t cáº£ bÃ¡o cÃ¡o sai!*
""",
        "image": "media/images/tai_khoan.jpg"
    },
    
    5: {
        "title": "ðŸ“‚ DANH Má»¤C â€“ PHÃ‚N LOáº I CHI TIÃŠU",
        "content": """
**ðŸŽ¯ Má»¥c tiÃªu: Hiá»ƒu tiá»n Ä‘i Ä‘Ã¢u, vÃ o Ä‘Ã¢u**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“‚ VÃ Dá»¤ DANH Má»¤C:**

**Chi tiÃªu:**
â€¢ ðŸœ Ä‚n uá»‘ng
â€¢ ðŸ  NhÃ  á»Ÿ
â€¢ ðŸŽ“ GiÃ¡o dá»¥c
â€¢ ðŸŽ‰ Giáº£i trÃ­
â€¢ ðŸš— Di chuyá»ƒn
â€¢ ðŸ‘¨â€âš•ï¸ Sá»©c khá»e

**Thu nháº­p:**
â€¢ ðŸ’¼ LÆ°Æ¡ng
â€¢ ðŸ’° Kinh doanh
â€¢ ðŸŽ QuÃ  táº·ng

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“‹ CÃCH LÃ€M:**

1ï¸âƒ£ VÃ o má»¥c **Categories**

2ï¸âƒ£ ThÃªm cÃ¡c danh má»¥c phÃ¹ há»£p vá»›i cuá»™c sá»‘ng

3ï¸âƒ£ Khi ghi giao dá»‹ch â†’ chá»n danh má»¥c

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**âœ… Káº¾T QUáº¢:**
â€¢ BÃ¡o cÃ¡o chi tiÃªu theo danh má»¥c
â€¢ Nháº­n diá»‡n "lá»— há»•ng" tiá»n
â€¢ Cáº¯t giáº£m chi tiÃªu hiá»‡u quáº£

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ’¡ Tip:**
*Danh má»¥c chi tiáº¿t â†’ phÃ¢n tÃ­ch tá»‘t hÆ¡n!*
""",
        "image": "media/images/danh_muc.jpg"
    },
    
    6: {
        "title": "ðŸ’³ KHOáº¢N Ná»¢ â€“ LÃ€M CHá»¦ Ná»¢",
        "content": """
**ðŸŽ¯ Má»¥c tiÃªu: KhÃ´ng nÃ© trÃ¡nh - chá»§ Ä‘á»™ng lÃ m chá»§ ná»£**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ’³ CÃ“ THá»‚ QUáº¢N LÃ:**

â€¢ Ná»£ vay ngÃ¢n hÃ ng
â€¢ Tráº£ gÃ³p (xe, nhÃ , Ä‘iá»‡n thoáº¡i)
â€¢ Ná»£ cÃ¡ nhÃ¢n
â€¢ Tháº» tÃ­n dá»¥ng

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“‹ CÃCH LÃ€M:**

1ï¸âƒ£ VÃ o má»¥c **Debts** (Khoáº£n ná»£)

2ï¸âƒ£ ThÃªm táº¥t cáº£ khoáº£n ná»£ hiá»‡n táº¡i

3ï¸âƒ£ Nháº­p: Sá»‘ tiá»n gá»‘c, lÃ£i suáº¥t, ká»³ háº¡n

4ï¸âƒ£ Cáº­p nháº­t khi tráº£ ná»£

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**âœ… Káº¾T QUáº¢:**
â€¢ Biáº¿t chÃ­nh xÃ¡c tá»•ng ná»£
â€¢ CÃ³ chiáº¿n lÆ°á»£c thoÃ¡t ná»£
â€¢ Giáº£m stress tÃ i chÃ­nh

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ’¡ Mindset:**
*"Ná»£ khÃ´ng pháº£i káº» thÃ¹ - khÃ´ng biáº¿t mÃ¬nh ná»£ bao nhiÃªu má»›i lÃ  káº» thÃ¹"*
""",
        "image": "media/images/khoan_no.jpg"
    },
    
    7: {
        "title": "ðŸ“ˆ Äáº¦U TÆ¯ â€“ TIá»€N LÃ€M VIá»†C CHO Báº N",
        "content": """
**ðŸŽ¯ Má»¥c tiÃªu: Theo dÃµi cÃ¡c khoáº£n Ä‘áº§u tÆ° hiá»‡u quáº£**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“ˆ CÃ“ THá»‚ TRACKING:**

â€¢ Chá»©ng khoÃ¡n (cá»• phiáº¿u, quá»¹)
â€¢ VÃ ng
â€¢ Báº¥t Ä‘á»™ng sáº£n cho thuÃª
â€¢ Kinh doanh
â€¢ Crypto

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“‹ CÃCH LÃ€M:**

1ï¸âƒ£ VÃ o má»¥c **Investments**

2ï¸âƒ£ ThÃªm tá»«ng khoáº£n Ä‘áº§u tÆ°

3ï¸âƒ£ Nháº­p: Vá»‘n gá»‘c, giÃ¡ trá»‹ hiá»‡n táº¡i

4ï¸âƒ£ Cáº­p nháº­t Ä‘á»‹nh ká»³ â†’ Xem ROI

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**âœ… Káº¾T QUáº¢:**
â€¢ Biáº¿t Ä‘áº§u tÆ° lÃ£i/lá»— bao nhiÃªu
â€¢ Quyáº¿t Ä‘á»‹nh dá»±a trÃªn sá»‘ liá»‡u
â€¢ Quáº£n lÃ½ portfolio hiá»‡u quáº£

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ’¡ LÆ°u Ã½:**
*Chá»‰ lÃ  cÃ´ng cá»¥ tracking - khÃ´ng pháº£i tÆ° váº¥n Ä‘áº§u tÆ°!*
""",
        "image": "media/images/dau_tu.jpg"
    },
    
    8: {
        "title": "ðŸ  TÃ€I Sáº¢N â€“ TÃNH NET WORTH",
        "content": """
**ðŸŽ¯ Má»¥c tiÃªu: Biáº¿t giÃ¡ trá»‹ thá»±c sá»± cá»§a báº¡n**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ  VÃ Dá»¤ TÃ€I Sáº¢N:**

â€¢ NhÃ  Ä‘áº¥t
â€¢ Xe (Ã´ tÃ´, xe mÃ¡y)
â€¢ Trang sá»©c, vÃ ng
â€¢ Äá»“ Ä‘iá»‡n tá»­ giÃ¡ trá»‹
â€¢ TÃ i sáº£n khÃ¡c

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“‹ CÃCH LÃ€M:**

1ï¸âƒ£ VÃ o má»¥c **Assets**

2ï¸âƒ£ ThÃªm táº¥t cáº£ tÃ i sáº£n lá»›n

3ï¸âƒ£ Nháº­p: GiÃ¡ mua, giÃ¡ hiá»‡n táº¡i

4ï¸âƒ£ Cáº­p nháº­t Ä‘á»‹nh ká»³

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**âœ… Káº¾T QUáº¢:**
â€¢ TÃ­nh Ä‘Æ°á»£c **Net Worth**
â€¢ Biáº¿t mÃ¬nh "giÃ u" tháº­t sá»± chÆ°a
â€¢ Theo dÃµi tÄƒng trÆ°á»Ÿng tÃ i sáº£n

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ’¡ CÃ´ng thá»©c vÃ ng:**
```
Net Worth = TÃ i sáº£n - Ná»£
```

*Thu nháº­p cao â‰  GiÃ u*
*GiÃ u = Net Worth cao!*
""",
        "image": "media/images/tai_san.jpg"
    },
    
    9: {
        "title": "ðŸŽ¯ Káº¾T LUáº¬N â€“ Tá»”NG QUAN",
        "content": """
**ðŸ† NGUYÃŠN Táº®C VÃ€NG KHI DÃ™NG FREEDOM WALLET:**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

1ï¸âƒ£ **Ghi chÃ©p HÃ€NG NGÃ€Y**
   â†’ Má»—i giao dá»‹ch pháº£i Ä‘Æ°á»£c ghi láº¡i

2ï¸âƒ£ **Xem bÃ¡o cÃ¡o HÃ€NG TUáº¦N**
   â†’ Kiá»ƒm tra chi tiÃªu, Ä‘iá»u chá»‰nh ká»‹p thá»i

3ï¸âƒ£ **ÄÃ¡nh giÃ¡ tÃ i chÃ­nh Má»–I THÃNG**
   â†’ Xem tá»•ng quan, so sÃ¡nh vá»›i thÃ¡ng trÆ°á»›c

4ï¸âƒ£ **Äiá»u chá»‰nh má»¥c tiÃªu Má»–I QUÃ**
   â†’ Thay Ä‘á»•i % 6 hÅ© náº¿u cáº§n

5ï¸âƒ£ **KiÃªn trÃ¬ ÃT NHáº¤T 90 NGÃ€Y**
   â†’ Äá»§ Ä‘á»ƒ hÃ¬nh thÃ nh thÃ³i quen

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸŒ± CÃ¢u nÃ³i cuá»‘i:**

*"Tá»± do tÃ i chÃ­nh khÃ´ng Ä‘áº¿n tá»« may máº¯n*
*â€“ mÃ  Ä‘áº¿n tá»« há»‡ thá»‘ng."*

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŽ‰ **ChÃºc báº¡n thÃ nh cÃ´ng trÃªn hÃ nh trÃ¬nh tá»± do tÃ i chÃ­nh!**
""",
        "image": "media/images/tong_quan.jpg"
    }
}


def get_setup_guide_keyboard(current_step: int) -> InlineKeyboardMarkup:
    """Generate navigation keyboard for setup guide"""
    buttons = []
    
    # Navigation row
    nav_row = []
    if current_step > 0:
        nav_row.append(InlineKeyboardButton("â¬…ï¸ Quay láº¡i", callback_data=f"guide_step_{current_step-1}"))
    
    if current_step < 9:
        nav_row.append(InlineKeyboardButton("Tiáº¿p theo âž¡ï¸", callback_data=f"guide_step_{current_step+1}"))
    
    if nav_row:
        buttons.append(nav_row)
    
    # Jump to specific sections (only show on step 0)
    if current_step == 0:
        buttons.append([
            InlineKeyboardButton("âš™ï¸ CÃ i Ä‘áº·t (1-3)", callback_data="guide_step_1"),
            InlineKeyboardButton("ðŸ’³ Tracking (4-8)", callback_data="guide_step_4")
        ])
    
    # Menu row
    menu_row = []
    if current_step != 0:
        menu_row.append(InlineKeyboardButton("ðŸ“˜ Menu", callback_data="guide_step_0"))
    
    if current_step == 9:
        menu_row.append(InlineKeyboardButton("âœ… HoÃ n thÃ nh", callback_data="guide_complete"))
    
    if menu_row:
        buttons.append(menu_row)
    
    # Help row (always available)
    buttons.append([
        InlineKeyboardButton("ðŸ’¬ Cáº§n trá»£ giÃºp?", url="https://t.me/freedomwalletapp")
    ])
    
    return InlineKeyboardMarkup(buttons)


async def send_guide_step(update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
    """Send a specific guide step"""
    try:
        if step not in SETUP_GUIDE_STEPS:
            await update.callback_query.answer("âŒ BÆ°á»›c khÃ´ng há»£p lá»‡!")
            return
        
        guide_data = SETUP_GUIDE_STEPS[step]
        keyboard = get_setup_guide_keyboard(step)
        
        message_text = f"{guide_data['title']}\n\n{guide_data['content']}"
        
        # Handle image + text combination
        if guide_data.get('image'):
            # If there's an image, we need to delete old message and send new photo message
            if update.callback_query:
                # Delete the old message
                await update.callback_query.message.delete()
                
                # Send new photo message
                with open(guide_data['image'], 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                await update.callback_query.answer()
            else:
                # Command: send photo directly
                with open(guide_data['image'], 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
        else:
            # No image, just text
            if update.callback_query:
                # Check if previous message was a photo
                if update.callback_query.message.photo:
                    # Previous was photo, need to delete and send new text message
                    await update.callback_query.message.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                    await update.callback_query.answer()
                else:
                    # Previous was text, can edit
                    await update.callback_query.edit_message_text(
                        text=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                    await update.callback_query.answer()
            else:
                await update.message.reply_text(
                    text=message_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
        
        logger.info(f"Sent guide step {step} to user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error sending guide step {step}: {e}")
        if update.callback_query:
            await update.callback_query.answer("âŒ CÃ³ lá»—i xáº£y ra!")


async def huongdan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /huongdan command"""
    await send_guide_step(update, context, step=0)


async def guide_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle guide navigation callbacks"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        if callback_data.startswith("guide_step_"):
            step = int(callback_data.split("_")[-1])
            await send_guide_step(update, context, step)
        
        elif callback_data == "guide_complete":
            # Delete photo message from step 9 before sending text
            await query.message.delete()
            
            # Send completion message with next steps
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="ðŸŽ‰ **CHÃšC Má»ªNG! Báº N ÄÃƒ HOÃ€N THÃ€NH HÆ¯á»šNG DáºªN!**\n\n"
                     "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
                     "âœ… **Báº¡n Ä‘Ã£ há»c Ä‘Æ°á»£c:**\n"
                     "â€¢ CÃ¡ch cÃ i Ä‘áº·t vÃ  xÃ³a dá»¯ liá»‡u máº«u\n"
                     "â€¢ Thiáº¿t láº­p 6 HÅ© Tiá»n vÃ  5 Cáº¥p báº­c\n"
                     "â€¢ Quáº£n lÃ½ TÃ i khoáº£n, Danh má»¥c, Ná»£, Äáº§u tÆ°, TÃ i sáº£n\n\n"
                     "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
                     "ðŸš€ **BÆ¯á»šC TIáº¾P THEO - HÃ€NH Äá»˜NG NGAY:**\n\n"
                     "**1ï¸âƒ£ Ghi giao dá»‹ch Ä‘áº§u tiÃªn** (Quan trá»ng nháº¥t!)\n"
                     "   â†’ Má»Ÿ Web App cá»§a báº¡n (link á»Ÿ Day 1)\n"
                     "   â†’ Thá»­ ghi 1 khoáº£n chi tiÃªu hÃ´m nay\n\n"
                     "**2ï¸âƒ£ Thiáº¿t láº­p 6 HÅ© Tiá»n cá»§a báº¡n**\n"
                     "   â†’ Settings â†’ 6 Jars â†’ Äiá»u chá»‰nh %\n\n"
                     "**3ï¸âƒ£ Nháº­p sá»‘ dÆ° tÃ i khoáº£n chÃ­nh xÃ¡c**\n"
                     "   â†’ Accounts â†’ ThÃªm táº¥t cáº£ tÃ i khoáº£n\n\n"
                     "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
                     "ðŸ’Ž **CAM Káº¾T 7 NGÃ€Y Äáº¦U TIÃŠN:**\n"
                     "Má»—i ngÃ y báº¡n sáº½ nháº­n Ä‘Æ°á»£c:\n"
                     "â€¢ 1 bÃ i há»c thá»±c táº¿ vá» quáº£n lÃ½ tÃ i chÃ­nh\n"
                     "â€¢ 1 nhiá»‡m vá»¥ nhá» Ä‘á»ƒ thá»±c hÃ nh\n"
                     "â€¢ Äá»™ng lá»±c vÃ  nháº¯c nhá»Ÿ tá»« bot\n\n"
                     "ðŸŽ¯ **Má»¥c tiÃªu:** Ghi chÃ©p Ä‘á»§ 7 ngÃ y â†’ HÃ¬nh thÃ nh thÃ³i quen!\n\n"
                     "ðŸ”¥ **Tham gia Group Ä‘á»ƒ:**\n"
                     "â€¢ ÄÆ°á»£c há»— trá»£ trá»±c tiáº¿p khi gáº·p khÃ³ khÄƒn\n"
                     "â€¢ Há»c há»i kinh nghiá»‡m tá»« cá»™ng Ä‘á»“ng\n"
                     "â€¢ Nháº­n tips & tricks Ä‘á»™c quyá»n\n"
                     "â€¢ Tham gia thá»­ thÃ¡ch 30 ngÃ y ghi chÃ©p\n\n"
                     "ðŸ’ª **Báº¯t Ä‘áº§u ngay hÃ´m nay - TÆ°Æ¡ng lai sáº½ cáº£m Æ¡n báº¡n!**",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("ðŸ‘¥ Tham gia Group VIP", url="https://t.me/freedomwalletapp")],
                    [InlineKeyboardButton("ðŸ“– Xem láº¡i hÆ°á»›ng dáº«n", callback_data="guide_step_0")],
                    [InlineKeyboardButton("ðŸ’¬ Chat vá»›i Admin", url="https://t.me/freedomwalletapp")]
                ])
            )
            await query.answer("ðŸŽ‰ HoÃ n thÃ nh! Báº¯t Ä‘áº§u ghi chÃ©p ngay nhÃ©!")
        
    except Exception as e:
        logger.error(f"Error in guide callback handler: {e}")
        await query.answer("âŒ CÃ³ lá»—i xáº£y ra!")


def register_setup_guide_handlers(application):
    """Register all setup guide handlers"""
    application.add_handler(CommandHandler("huongdan", huongdan_command))
    application.add_handler(CallbackQueryHandler(guide_callback_handler, pattern="^guide_"))
    
    logger.info("âœ… Setup guide handlers registered")

