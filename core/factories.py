import factory
from factory.declarations import SubFactory
from core.models import Tag, Ingredient, Recipe


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag-{n}")
    # email = factory.LazyAttribute(lambda a: '{}.{}@example.com'.format(a.first_name, a.last_name).lower())


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient

    name = factory.Sequence(lambda n: f"ingredient-{n}")


class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recipe

    title = factory.Sequence(lambda n: f"recipe-{n}")
    time_minutes = factory.faker.Faker("pyint")
    price = factory.faker.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=500)
    link = factory.faker.Faker("url")
    # image = factory.django.ImageField(color="blue")

    @factory.post_generation
    def ingredients(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for ingredient in extracted:
                self.ingredients.add(ingredient)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)
