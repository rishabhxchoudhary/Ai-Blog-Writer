#!/usr/bin/env python3
"""
Database setup script for Blog Writer application.
Creates the necessary tables for storing trends data.
"""

import asyncio
import asyncpg
import sys


async def create_database_schema():
    """Create the database schema for trends"""
    
    # Database connection parameters
    DSN = "postgresql://blog:pw@localhost/blog"
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DSN)
        
        # Create trends table
        create_trends_table = """
        CREATE TABLE IF NOT EXISTS trends (
            id VARCHAR(32) PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT,
            source VARCHAR(50) NOT NULL,
            score INTEGER NOT NULL,
            ts TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create index for faster queries
        create_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_trends_source ON trends(source);",
            "CREATE INDEX IF NOT EXISTS idx_trends_score ON trends(score);", 
            "CREATE INDEX IF NOT EXISTS idx_trends_ts ON trends(ts);",
            "CREATE INDEX IF NOT EXISTS idx_trends_created_at ON trends(created_at);"
        ]
        
        print("Creating trends table...")
        await conn.execute(create_trends_table)
        print("✅ Trends table created successfully")
        
        print("Creating indexes...")
        for index_sql in create_indexes:
            await conn.execute(index_sql)
        print("✅ Indexes created successfully")
        
        # Verify table was created
        result = await conn.fetchval(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'trends'"
        )
        
        if result == 1:
            print("✅ Database schema setup completed successfully")
        else:
            print("❌ Error: trends table was not created")
            
    except asyncpg.ConnectionError as e:
        print(f"❌ Database connection error: {e}")
        print("Make sure PostgreSQL is running and the database 'blog' exists")
        print("You may need to run: createdb blog")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)
        
    finally:
        if 'conn' in locals():
            await conn.close()


async def verify_schema():
    """Verify the database schema is set up correctly"""
    DSN = "postgresql://blog:pw@localhost/blog"
    
    try:
        conn = await asyncpg.connect(DSN)
        
        # Check if trends table exists and get its structure
        table_info = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'trends'
            ORDER BY ordinal_position;
        """)
        
        if not table_info:
            print("❌ Trends table not found")
            return False
            
        print("\n📋 Trends table structure:")
        for row in table_info:
            nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  {row['column_name']}: {row['data_type']} {nullable}")
            
        # Check indexes
        indexes = await conn.fetch("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'trends'
            AND indexname != 'trends_pkey';
        """)
        
        print(f"\n📊 Indexes ({len(indexes)} found):")
        for idx in indexes:
            print(f"  {idx['indexname']}")
            
        print("✅ Schema verification completed")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            await conn.close()


async def main():
    """Main function"""
    print("🚀 Setting up Blog Writer database schema...")
    print("=" * 50)
    
    await create_database_schema()
    await verify_schema()
    
    print("\n🎉 Database setup completed!")
    print("\nYou can now run the Trend Scout agent:")
    print("  python agents/trend_scout.py")


if __name__ == "__main__":
    asyncio.run(main())
