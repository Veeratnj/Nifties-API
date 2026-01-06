from app.db.db import SessionLocal
from app.models.models import HistoricalData
import pandas as pd

file = r'hist\SENSEX_3min.csv'  # raw string for Windows path


def insert_csv_records(token='51', timeframe='THREE_MIN'):
    df = pd.read_csv(file)

    session = SessionLocal()
    try:
        for _, row in df.iterrows():
            record = HistoricalData(
                symbol=token,
                timeframe=timeframe,
                timestamp=row['start_time'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume'],
            )

            session.add(record)

        session.commit()
        print("✅ CSV data inserted successfully")

    except Exception as e:
        session.rollback()
        print("❌ Error:", e)

    finally:
        session.close()


insert_csv_records()
