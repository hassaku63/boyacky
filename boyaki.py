from pynamodb.attributes import UnicodeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.models import Model


class ViewIndex(GlobalSecondaryIndex):
    class Meta:
        projection = AllProjection()
    date = UnicodeAttribute(hash_key=True)
    time = UnicodeAttribute(range_key=True)


class Boyaki(Model):
    class Meta:
        import boto3
        region = boto3.session.Session().region_name
        table_name = 'boyacky'
        billing_mode = 'PAY_PER_REQUEST'

    id = UnicodeAttribute(hash_key=True)
    date = UnicodeAttribute()
    time = UnicodeAttribute()
    boyaki = UnicodeAttribute()
    view_index = ViewIndex()
