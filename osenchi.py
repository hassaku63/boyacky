import csv
import os
import boto3
from datetime import timedelta
from datetime import datetime as dt
from typing import List
from boyaki import Boyaki

s3 = boto3.resource('s3')
comprehend = boto3.client('comprehend')


def get_boyaki(hash_key: str) -> List[Boyaki]:
    result = Boyaki.view_index.query(hash_key, scan_index_forward=False)
    try:
        items = list(result)
    except Exception:
        items = []
    return items


def save_boyaki(items: List[Boyaki], file_path: str):
    with open(file_path, 'w', encoding='shift_jis') as fp:
        writer = csv.writer(fp)
        writer.writerow(['ID', 'Date', 'Boyaki', 'Sentiment',
                         'Positive', 'Negative', 'Neutral'])
        for item in items:
            result = comprehend.detect_sentiment(
                Text=item.boyaki, LanguageCode='ja')
            sentiment = result['Sentiment']
            score = result['SentimentScore']
            row = [item.id, f'{item.date} {item.time}',
                   item.boyaki, sentiment,
                   round(score['Positive'], 8),
                   round(score['Negative'], 8),
                   round(score['Neutral'], 8)]
            print(row)
            writer.writerow(row)


def put_boyaki(file_path: str, bucket_name: str):
    dest_name = os.path.basename(file_path)
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file(file_path, dest_name)


def execute(bucket_name: str, days: int = 0):
    hash_key = (dt.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    items = get_boyaki(hash_key)
    if len(items) > 0:
        file_path = f'/tmp/{hash_key}.csv'
        save_boyaki(items, file_path)
        put_boyaki(file_path, bucket_name)


if __name__ == '__main__':
    try:
        if not Boyaki.exists():
            Boyaki.create_table(wait=True)
        bucket_name = os.getenv('EXPORT_BUCKET')
        execute(bucket_name)
    except Exception as ex:
        print('error:', ex)
