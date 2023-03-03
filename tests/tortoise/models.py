from tortoise.models import Model
from tortoise import fields


class BaseModel(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class Tournament(BaseModel):
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name


class Event(BaseModel):
    name = fields.CharField(max_length=255)

    tournament = fields.ForeignKeyField('models.Tournament', related_name='events')
    participants = fields.ManyToManyField('models.User', related_name='events')

    def __str__(self):
        return self.name


class User(BaseModel):
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)

    def __str__(self):
        return self.username
