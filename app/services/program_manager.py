"""
🎯 PROGRAM MANAGER
==================

Manages user enrollment in educational programs with flexible day-by-day progression.

Programs:
- NURTURE_7_DAY: Daily encouragement for 0-1 refs users
- ONBOARDING_7_DAY: Welcome journey for new VIP users
- ADVANCED_WORKSHOP: Week 3-4 (future)
- MENTOR_PROGRAM: Week 4+ (future)

Strategy (Week 3):
- Convert existing campaigns to programs
- Maintain existing message content
- Add enrollment/completion tracking
- No changes to user experience

Author: Freedom Wallet Team
Version: 2.0 (Week 3 - Program Manager)
Date: 2026-02-08
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from telegram.ext import ContextTypes
from app.utils.database import SessionLocal, User
from loguru import logger


class ProgramType(str, Enum):
    """Available programs"""
    NURTURE_7_DAY = "NURTURE_7_DAY"  # For REGISTERED users (0-1 refs)
    ONBOARDING_7_DAY = "ONBOARDING_7_DAY"  # For new VIP users
    ADVANCED_WORKSHOP = "ADVANCED_WORKSHOP"  # Future: Week 3-4
    MENTOR_PROGRAM = "MENTOR_PROGRAM"  # Future: Week 4+
    REACTIVATION = "REACTIVATION"  # Future: For churned users


class ProgramManager:
    """
    Central program management with enrollment tracking
    
    Usage:
        pm = ProgramManager()
        await pm.enroll_user(user_id, ProgramType.NURTURE_7_DAY, context)
        await pm.advance_program_day(user_id, context)
    """
    
    def __init__(self):
        self.session = SessionLocal()
    
    async def enroll_user(
        self, 
        user_id: int, 
        program: ProgramType,
        context: ContextTypes.DEFAULT_TYPE,
        force: bool = False,
        initial_delay_minutes: int = 0
    ) -> bool:
        """
        Enroll user in a program
        
        Args:
            user_id: Telegram user ID
            program: Program to enroll in
            context: Telegram context for scheduling
            force: If True, override current program
            initial_delay_minutes: Delay before sending Day 1 (0 = immediate)
        
        Returns:
            Success status
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"Cannot enroll user {user_id}: not found")
            return False
        
        # Check if already enrolled
        if user.current_program and not force:
            logger.info(f"User {user_id} already in {user.current_program}, skipping enrollment")
            return False
        
        # Cancel existing program if force=True
        if user.current_program and force:
            logger.info(f"Force-enrolling user {user_id}: canceling {user.current_program}")
            await self._cancel_program(user_id, context)
        
        # Enroll in new program
        user.current_program = program.value
        user.program_day = 0
        user.program_started_at = datetime.utcnow()
        user.program_completed_at = None
        self.session.commit()
        
        logger.info(f"✅ User {user_id} enrolled in {program.value}")
        
        # Schedule first day immediately or with delay
        await self._schedule_program_day(
            user_id, 
            program, 
            day=1, 
            context=context,
            extra_delay_minutes=initial_delay_minutes
        )
        
        return True
    
    async def advance_program_day(
        self, 
        user_id: int,
        context: ContextTypes.DEFAULT_TYPE
    ) -> Optional[int]:
        """
        Advance user to next program day
        
        Returns:
            New day number, or None if program completed
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user or not user.current_program:
            return None
        
        program = ProgramType(user.current_program)
        current_day = user.program_day
        next_day = current_day + 1
        
        # Check if program completed
        max_days = self._get_program_max_days(program)
        if next_day > max_days:
            await self.complete_program(user_id)
            return None
        
        # Advance day
        user.program_day = next_day
        self.session.commit()
        
        logger.info(f"📈 User {user_id} advanced to {program.value} day {next_day}")
        
        # Schedule next day
        await self._schedule_program_day(user_id, program, next_day, context)
        
        return next_day
    
    async def complete_program(self, user_id: int) -> bool:
        """
        Mark program as completed
        
        Note: Does NOT change user_state (state changes from actions, not programs)
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user or not user.current_program:
            return False
        
        program = user.current_program
        user.current_program = None
        user.program_day = 0
        user.program_completed_at = datetime.utcnow()
        self.session.commit()
        
        logger.info(f"🎉 User {user_id} completed {program}")
        
        return True
    
    async def cancel_program(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Cancel current program (public method)
        """
        return await self._cancel_program(user_id, context)
    
    async def _cancel_program(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Cancel current program and remove scheduled jobs
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user or not user.current_program:
            return False
        
        program = user.current_program
        
        # Remove scheduled jobs
        job_prefix = f"program_{user_id}_"
        current_jobs = context.job_queue.get_jobs_by_name(job_prefix)
        for job in current_jobs:
            job.schedule_removal()
        
        # Clear program data
        user.current_program = None
        user.program_day = 0
        self.session.commit()
        
        logger.info(f"❌ Canceled {program} for user {user_id}")
        
        return True
    
    async def _schedule_program_day(
        self, 
        user_id: int,
        program: ProgramType,
        day: int,
        context: ContextTypes.DEFAULT_TYPE,
        extra_delay_minutes: int = 0
    ):
        """
        Schedule a specific program day message
        
        Args:
            extra_delay_minutes: Additional delay for this specific day (e.g., Day 1 VIP unlock)
        """
        # Get program config
        config = self._get_program_config(program)
        
        if day not in config:
            logger.warning(f"Day {day} not found in {program.value} config")
            return
        
        day_config = config[day]
        delay_hours = day_config.get("delay_hours", 0)
        
        # Calculate send time with extra delay if specified
        total_delay_hours = delay_hours + (extra_delay_minutes / 60.0)
        
        if total_delay_hours == 0:
            send_time = datetime.utcnow()
        else:
            send_time = datetime.utcnow() + timedelta(hours=total_delay_hours)
        
        # Schedule job
        job_name = f"program_{user_id}_{program.value}_day_{day}"
        
        context.job_queue.run_once(
            self._send_program_message,
            when=send_time,
            data={
                "user_id": user_id,
                "program": program.value,
                "day": day,
                "config": day_config
            },
            name=job_name
        )
        
        logger.info(f"📅 Scheduled {program.value} day {day} for user {user_id} at {send_time}")
    
    async def _send_program_message(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Send program message (called by job queue)
        """
        job_data = context.job.data
        user_id = job_data["user_id"]
        program = job_data["program"]
        day = job_data["day"]
        config = job_data["config"]
        
        # Get message from config
        messages = self._get_program_config(ProgramType(program))
        if day not in messages:
            logger.warning(f"No message for {program} day {day}")
            return
            
        message_data = messages[day]
        
        # Send message using messaging service
        from app.services.messaging_service import send_program_message
        await send_program_message(context, user_id, message_data["content"])
    
    def _get_program_config(self, program: ProgramType) -> Dict[int, Dict[str, Any]]:
        """
        Get program configuration (message content, delays, etc.)
        
        Note: Content is still in daily_nurture.py and onboarding.py
        This just returns the structure
        """
        if program == ProgramType.NURTURE_7_DAY:
            from app.messages.nurture_messages import NURTURE_MESSAGES
            return NURTURE_MESSAGES
        
        elif program == ProgramType.ONBOARDING_7_DAY:
            from app.messages.onboarding_messages import ONBOARDING_MESSAGES
            return ONBOARDING_MESSAGES
        
        else:
            logger.warning(f"No config for program: {program.value}")
            return {}
    
    def _get_program_max_days(self, program: ProgramType) -> int:
        """Get maximum days for program"""
        config = self._get_program_config(program)
        return len(config) if config else 0
    
    def get_user_program_status(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user's current program status
        
        Returns:
            {
                "program": "NURTURE_7_DAY",
                "day": 3,
                "started_at": datetime,
                "progress": "3/7"
            }
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user or not user.current_program:
            return None
        
        program = ProgramType(user.current_program)
        max_days = self._get_program_max_days(program)
        
        return {
            "program": user.current_program,
            "day": user.program_day,
            "started_at": user.program_started_at,
            "progress": f"{user.program_day}/{max_days}",
            "max_days": max_days
        }
    
    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def enroll_user_in_program(
    user_id: int, 
    program: ProgramType,
    context: ContextTypes.DEFAULT_TYPE,
    force: bool = False
) -> bool:
    """
    Convenience function to enroll user in program
    
    Usage:
        from app.services.program_manager import enroll_user_in_program, ProgramType
        success = await enroll_user_in_program(user_id, ProgramType.NURTURE_7_DAY, context)
    """
    with ProgramManager() as pm:
        return await pm.enroll_user(user_id, program, context, force)


async def cancel_user_program(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Convenience function to cancel user's current program
    """
    with ProgramManager() as pm:
        return await pm.cancel_program(user_id, context)


def get_program_status(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get program status
    """
    with ProgramManager() as pm:
        return pm.get_user_program_status(user_id)

