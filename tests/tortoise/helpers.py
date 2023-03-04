from tortoise import Tortoise

from tests.tortoise import models
from tests.tortoise import admins

async def tortoise_init_db_connection():
    await Tortoise.init(
        db_url='sqlite://:memory:',
        modules={'models': ['tests.tortoise.models']}
    )
    await Tortoise.generate_schemas()
    return Tortoise.get_connection('default')


async def tortoise_close_db_connection():
    await Tortoise.close_connections()


async def tortoise_create_objects():
    superuser = await models.User.create(username='Test SuperUser', password='password', is_superuser=True)
    user = await models.User.create(username='Test User', password='password')
    tournament = await models.Tournament.create(name='Test Tournament')
    event = await models.Event.create(name='Test Event', tournament=tournament)
    await event.participants.add(user)
    return {
        "superuser": superuser,
        "user": user,
        "tournament": tournament,
        "event": event,
        "admin_user_cls": admins.UserAdmin,
        "admin_tournament_cls": admins.TournamentAdmin,
        "admin_event_cls": admins.EventAdmin,
    }


async def tortoise_delete_objects():
    await models.User.all().delete()
    await models.Tournament.all().delete()
    await models.Event.all().delete()
