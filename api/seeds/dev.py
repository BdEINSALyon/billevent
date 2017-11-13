import random
from datetime import datetime, timedelta

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
from django_seed import Seed

seeder = Seed.seeder()
from django.contrib.auth.models import Group, User

user = User(username="root", is_staff=True, is_superuser=True)
user.set_password("root")
user.save()

seeder.add_entity(Group, 5)
seeder.execute()

from api import models

seeder = Seed.seeder()

# event = models.Event(
#     name="Gala",
#     description="Hellow World, this is not a real description",
#     sales_opening=datetime.now(),
#     sales_closing=datetime.now()+timedelta(days=30),
#     max_seats=3500,
#     seats_goal=3200
# )
#
# event.save()

seeder.add_entity(models.Event, 1)
seeder.add_entity(models.Product, 5)
seeder.add_entity(models.Option, 2)

inserted_pks = seeder.execute()
