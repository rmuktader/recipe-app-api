import factory
from django.contrib.auth import get_user_model
from core.models import Tag, Ingredient, Recipe


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag-{n}")


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
    image = factory.django.ImageField(color="blue")

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


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    name = factory.faker.Faker("name")
    email = factory.lazy_attribute(lambda a: f"{a.name.replace(' ', '.')}@test.com")
    is_active = True
    is_staff = False
