"""
Sync Landing Page users from Google Sheet into Bot Database
This ensures admin dashboard shows accurate user counts including landing page registrations
"""

import logging
from datetime import datetime, timezone, timedelta
from bot.utils.sheets_registration import get_registration_worksheet
from bot.utils.database import SessionLocal, User
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

VN_TZ = timezone(timedelta(hours=7))


async def sync_landing_page_users_to_db():
    """
    Pull all landing page registrations from Google Sheet and create shadow User records in bot DB.
    These are users who registered via freedomwallet.app but haven't used the Telegram bot yet.
    """
    try:
        worksheet = get_registration_worksheet()
        if not worksheet:
            logger.warning("Could not access registration worksheet for sync")
            return

        all_values = worksheet.get_all_values()
        if len(all_values) < 2:
            logger.info("No data in registration sheet")
            return

        db = SessionLocal()
        synced = 0
        skipped = 0

        for idx, row in enumerate(all_values[1:], start=2):  # Skip header
            try:
                # Parse row data
                reg_date_str = row[0].strip() if len(row) > 0 else ""
                user_id_str = row[1].strip() if len(row) > 1 else ""
                username = row[2].strip() if len(row) > 2 else ""
                full_name = row[3].strip() if len(row) > 3 else ""
                email = row[4].strip() if len(row) > 4 else ""
                phone = row[5].strip() if len(row) > 5 else ""
                plan = row[6].strip() if len(row) > 6 else "FREE"
                referral_code = row[7].strip() if len(row) > 7 else ""
                source = row[9].strip() if len(row) > 9 else "Landing Page"
                status = row[10].strip() if len(row) > 10 else ""

                # Skip if not a landing page registration or if already has Telegram user_id
                if source != "Landing Page":
                    continue
                if user_id_str and user_id_str.isdigit() and int(user_id_str) > 100000:
                    # Already synced with bot (has real Telegram ID > 100k)
                    skipped += 1
                    continue

                # Check if we already created a shadow user for this email
                existing = db.query(User).filter(
                    User.email == email,
                    User.activation_source == "LANDING_PAGE"
                ).first()

                if existing:
                    skipped += 1
                    continue

                # Parse registration date (format: 22/02/2026 18:04:25)
                first_seen = None
                if reg_date_str:
                    try:
                        # Parse DD/MM/YYYY HH:MM:SS
                        dt = datetime.strptime(reg_date_str, "%d/%m/%Y %H:%M:%S")
                        # Assume sheet times are VN timezone
                        first_seen = dt.replace(tzinfo=VN_TZ).astimezone(timezone.utc)
                    except ValueError:
                        pass

                # Create shadow user (fake Telegram ID using email hash)
                # Use negative ID to avoid collision with real Telegram IDs
                shadow_id = -(abs(hash(email)) % 1_000_000_000)  # Negative ID = landing page user

                new_user = User(
                    id=shadow_id,
                    username=username or None,
                    first_name=full_name or email.split("@")[0],
                    email=email,
                    phone=phone or None,
                    referral_code=referral_code or None,
                    activation_source="LANDING_PAGE",
                    user_status="PENDING",
                    is_registered=False,  # Not yet registered in bot
                    first_seen_at=first_seen or datetime.now(timezone.utc),
                    last_active=first_seen or datetime.now(timezone.utc),
                    admin_tag=f"LP: {status}" if status else "Landing Page",
                )

                db.add(new_user)
                try:
                    db.commit()
                    synced += 1
                    logger.info(f"✅ Synced landing page user: {email} (shadow ID {shadow_id})")
                except IntegrityError:
                    db.rollback()
                    skipped += 1
                    logger.debug(f"⏭️ Skipped duplicate: {email}")

            except Exception as e:
                logger.error(f"Error syncing row {idx}: {e}")
                db.rollback()
                continue

        db.close()
        logger.info(f"📊 Landing page sync complete: {synced} synced, {skipped} skipped")

    except Exception as e:
        logger.error(f"Error in sync_landing_page_users_to_db: {e}", exc_info=True)
