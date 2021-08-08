import factory
from core.models import Tag


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: "tag-{0}".format(n))
