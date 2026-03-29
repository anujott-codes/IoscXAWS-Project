import asyncio
import time
from app.core.database import SessionLocal
from sqlalchemy import text

async def db_health_check():
    print("Starting DB health check...\n")

    # Test 1 - basic connectivity
    try:
        start = time.time()
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        elapsed = time.time() - start
        print(f"✅ Connection OK        ({elapsed:.2f}s)")
    except Exception as e:
        print(f"❌ Connection FAILED    — {e}")
        return

    # Test 2 - simple query speed
    try:
        start = time.time()
        async with SessionLocal() as db:
            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
        elapsed = time.time() - start
        print(f"✅ Query OK             ({elapsed:.2f}s) — {count} total users")
    except Exception as e:
        print(f"❌ Query FAILED         — {e}")

    # Test 3 - write speed
    try:
        start = time.time()
        async with SessionLocal() as db:
            await db.execute(text("CREATE TEMP TABLE IF NOT EXISTS _ping (id SERIAL)"))
            await db.execute(text("INSERT INTO _ping DEFAULT VALUES"))
            await db.commit()
        elapsed = time.time() - start
        print(f"✅ Write OK             ({elapsed:.2f}s)")
    except Exception as e:
        print(f"❌ Write FAILED         — {e}")

    # Test 4 - latency (5 pings)
    print(f"\nRunning 5 ping tests...")
    times = []
    for i in range(5):
        try:
            start = time.time()
            async with SessionLocal() as db:
                await db.execute(text("SELECT 1"))
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  Ping {i+1}: {elapsed:.2f}s")
        except Exception as e:
            print(f"  Ping {i+1}: FAILED — {e}")

    if times:
        print(f"\nAvg latency : {sum(times)/len(times):.2f}s")
        print(f"Min latency : {min(times):.2f}s")
        print(f"Max latency : {max(times):.2f}s")

    print("\nHealth check complete.")

asyncio.run(db_health_check())