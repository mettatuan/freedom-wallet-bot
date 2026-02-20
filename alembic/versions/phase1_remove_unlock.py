"""Phase 1: Remove unlock system, add activation tracking

Revision ID: phase1_remove_unlock
Revises: 
Create Date: 2026-02-20

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'phase1_remove_unlock'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Remove unlock fields, add activation tracking fields"""
    
    # Add new activation tracking columns
    with op.batch_alter_table('users') as batch_op:
        # Add first_transaction_at (activation milestone)
        batch_op.add_column(sa.Column('first_transaction_at', sa.DateTime, nullable=True))
        
        # Add activated_at (same as first_transaction_at for simplicity)
        batch_op.add_column(sa.Column('activated_at', sa.DateTime, nullable=True))
        
        # Remove unlock fields
        batch_op.drop_column('is_free_unlocked')
        batch_op.drop_column('unlock_offered')
        batch_op.drop_column('unlock_offered_at')
    
    print("✅ Phase 1 migration completed:")
    print("   - Removed: is_free_unlocked, unlock_offered, unlock_offered_at")
    print("   - Added: first_transaction_at, activated_at")


def downgrade():
    """Rollback to unlock system"""
    
    with op.batch_alter_table('users') as batch_op:
        # Remove activation tracking columns
        batch_op.drop_column('first_transaction_at')
        batch_op.drop_column('activated_at')
        
        # Restore unlock columns
        batch_op.add_column(sa.Column('is_free_unlocked', sa.Boolean, default=False))
        batch_op.add_column(sa.Column('unlock_offered', sa.Boolean, default=False))
        batch_op.add_column(sa.Column('unlock_offered_at', sa.DateTime, nullable=True))
    
    print("❌ Rollback completed: Restored unlock system")
