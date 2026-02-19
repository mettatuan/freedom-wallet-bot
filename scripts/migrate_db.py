"""
Database Migration Script: SQLite -> PostgreSQL
Safely migrate data without loss
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from loguru import logger

# Setup logging
logger.add("data/logs/migration_{time}.log", rotation="10 MB")


class DatabaseMigration:
    """Handle database migration from SQLite to PostgreSQL"""
    
    def __init__(self, source_url: str = None, target_url: str = None):
        # Load from environment if not provided
        if not source_url:
            source_url = os.getenv("SOURCE_DB_URL", "sqlite:///data/bot.db")
        if not target_url:
            from config.settings import settings
            target_url = settings.DATABASE_URL
        
        self.source_url = source_url
        self.target_url = target_url
        
        logger.info(f"Source DB: {source_url}")
        logger.info(f"Target DB: {target_url[:30]}...")  # Don't log password
    
    def export_to_json(self, output_file: str = "data/db_export.json"):
        """Export all data from source database to JSON"""
        logger.info("🔄 Starting database export...")
        
        try:
            # Connect to source database
            source_engine = create_engine(self.source_url)
            metadata = MetaData()
            metadata.reflect(bind=source_engine)
            
            Session = sessionmaker(bind=source_engine)
            session = Session()
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "source_db": self.source_url,
                "tables": {}
            }
            
            # Export each table
            for table_name in metadata.tables.keys():
                table = metadata.tables[table_name]
                
                logger.info(f"  📦 Exporting table: {table_name}")
                
                # Get all rows
                result = session.execute(table.select())
                rows = result.fetchall()
                
                # Convert to dict
                export_data["tables"][table_name] = {
                    "row_count": len(rows),
                    "columns": [col.name for col in table.columns],
                    "data": [dict(row._mapping) for row in rows]
                }
                
                logger.info(f"    ✅ Exported {len(rows)} rows")
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.success(f"✅ Export completed: {output_file}")
            logger.info(f"   Tables exported: {len(export_data['tables'])}")
            
            total_rows = sum(t['row_count'] for t in export_data['tables'].values())
            logger.info(f"   Total rows: {total_rows}")
            
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return False
    
    def import_from_json(self, input_file: str = "data/db_export.json"):
        """Import data from JSON to target database"""
        logger.info("🔄 Starting database import...")
        
        try:
            # Load export file
            with open(input_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            logger.info(f"   Export date: {export_data['exported_at']}")
            logger.info(f"   Tables: {len(export_data['tables'])}")
            
            # Connect to target database
            target_engine = create_engine(self.target_url)
            
            # Create tables (assumes alembic has run)
            from app.database.models import Base  # Import your models
            Base.metadata.create_all(bind=target_engine)
            
            Session = sessionmaker(bind=target_engine)
            session = Session()
            
            # Import each table
            for table_name, table_data in export_data['tables'].items():
                logger.info(f"  📦 Importing table: {table_name}")
                
                metadata = MetaData()
                metadata.reflect(bind=target_engine)
                
                if table_name not in metadata.tables:
                    logger.warning(f"    ⚠️ Table {table_name} not found in target, skipping")
                    continue
                
                table = metadata.tables[table_name]
                
                # Insert rows
                if table_data['data']:
                    session.execute(table.insert(), table_data['data'])
                    session.commit()
                    logger.info(f"    ✅ Imported {len(table_data['data'])} rows")
                else:
                    logger.info(f"    ℹ️ No data to import")
            
            logger.success("✅ Import completed successfully!")
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Import failed: {e}")
            return False
    
    def verify_migration(self, export_file: str = "data/db_export.json"):
        """Verify migration success by comparing row counts"""
        logger.info("🔍 Verifying migration...")
        
        try:
            # Load original export
            with open(export_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            # Connect to target
            target_engine = create_engine(self.target_url)
            metadata = MetaData()
            metadata.reflect(bind=target_engine)
            
            Session = sessionmaker(bind=target_engine)
            session = Session()
            
            all_match = True
            
            for table_name, table_data in export_data['tables'].items():
                if table_name not in metadata.tables:
                    logger.warning(f"  ⚠️ Table {table_name} not in target DB")
                    continue
                
                table = metadata.tables[table_name]
                result = session.execute(table.select())
                target_count = len(result.fetchall())
                source_count = table_data['row_count']
                
                if target_count == source_count:
                    logger.success(f"  ✅ {table_name}: {target_count} rows (match)")
                else:
                    logger.error(f"  ❌ {table_name}: Source={source_count}, Target={target_count} (MISMATCH)")
                    all_match = False
            
            session.close()
            
            if all_match:
                logger.success("✅ Migration verified successfully!")
                return True
            else:
                logger.error("❌ Migration verification failed - row counts don't match")
                return False
                
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False


def main():
    """CLI interface for database migration"""
    parser = argparse.ArgumentParser(description="Database Migration Tool")
    parser.add_argument("command", choices=['export', 'import', 'verify'],
                       help="Migration command")
    parser.add_argument("--output", default="data/db_export.json",
                       help="Output file for export")
    parser.add_argument("--input", default="data/db_export.json",
                       help="Input file for import")
    parser.add_argument("--source", help="Source database URL")
    parser.add_argument("--target", help="Target database URL")
    
    args = parser.parse_args()
    
    migrator = DatabaseMigration(source_url=args.source, target_url=args.target)
    
    if args.command == 'export':
        success = migrator.export_to_json(args.output)
    elif args.command == 'import':
        success = migrator.import_from_json(args.input)
    elif args.command == 'verify':
        success = migrator.verify_migration(args.input)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
