import pytest
from apps.pantry.models import PantryItem
from apps.recipes.models import Ingredient


@pytest.fixture
def honey(db):
    return Ingredient.objects.create(name='Test Honey', type=Ingredient.TYPE_HONEY)


@pytest.fixture
def yeast(db):
    return Ingredient.objects.create(name='Test Yeast', type=Ingredient.TYPE_YEAST)


class TestPantryView:
    def test_requires_login(self, client):
        r = client.get('/pantry/')
        assert r.status_code == 302
        assert '/accounts/login/' in r['Location']

    def test_empty_pantry(self, auth_client):
        r = auth_client.get('/pantry/')
        assert r.status_code == 200
        assert b'pantry is empty' in r.content

    def test_add_existing_ingredient(self, auth_client, honey):
        r = auth_client.post('/pantry/', {
            'ingredient_name': 'Test Honey',
            'quantity': '5 lbs',
            'notes': '',
        })
        assert r.status_code == 302
        assert PantryItem.objects.filter(ingredient=honey).exists()

    def test_add_case_insensitive(self, auth_client, honey):
        auth_client.post('/pantry/', {'ingredient_name': 'test honey', 'quantity': ''})
        # Should link to existing ingredient, not create duplicate
        assert Ingredient.objects.filter(name__iexact='test honey').count() == 1

    def test_add_new_ingredient_creates_it(self, auth_client, db):
        auth_client.post('/pantry/', {
            'ingredient_name': 'Elderflower',
            'ingredient_type': Ingredient.TYPE_ADDITIVE,
            'quantity': '1 bag',
        })
        assert Ingredient.objects.filter(name='Elderflower').exists()
        assert PantryItem.objects.filter(ingredient__name='Elderflower').exists()

    def test_duplicate_add_does_not_create_two(self, auth_client, honey):
        auth_client.post('/pantry/', {'ingredient_name': 'Test Honey', 'quantity': '3 lbs'})
        auth_client.post('/pantry/', {'ingredient_name': 'Test Honey', 'quantity': '5 lbs'})
        assert PantryItem.objects.filter(ingredient=honey).count() == 1

    def test_shows_pantry_items(self, auth_client, user, honey):
        PantryItem.objects.create(user=user, ingredient=honey, quantity='2 lbs')
        r = auth_client.get('/pantry/')
        assert b'Test Honey' in r.content

    def test_empty_name_rejected(self, auth_client):
        r = auth_client.post('/pantry/', {'ingredient_name': '', 'quantity': '1 lb'})
        assert r.status_code == 302
        assert PantryItem.objects.count() == 0


class TestDeletePantryItem:
    def test_delete_own_item(self, auth_client, user, honey):
        item = PantryItem.objects.create(user=user, ingredient=honey)
        r = auth_client.post(f'/pantry/{item.pk}/delete/')
        assert r.status_code == 302
        assert not PantryItem.objects.filter(pk=item.pk).exists()

    def test_cannot_delete_other_users_item(self, auth_client, other_user, honey):
        item = PantryItem.objects.create(user=other_user, ingredient=honey)
        r = auth_client.post(f'/pantry/{item.pk}/delete/')
        assert r.status_code == 404
        assert PantryItem.objects.filter(pk=item.pk).exists()

    def test_get_not_allowed(self, auth_client, user, honey):
        item = PantryItem.objects.create(user=user, ingredient=honey)
        r = auth_client.get(f'/pantry/{item.pk}/delete/')
        assert r.status_code == 405


class TestEditPantryItem:
    def test_edit_quantity(self, auth_client, user, honey):
        item = PantryItem.objects.create(user=user, ingredient=honey, quantity='1 lb')
        auth_client.post(f'/pantry/{item.pk}/edit/', {'quantity': '5 lbs', 'notes': 'fresh'})
        item.refresh_from_db()
        assert item.quantity == '5 lbs'
        assert item.notes == 'fresh'

    def test_cannot_edit_other_users_item(self, auth_client, other_user, honey):
        item = PantryItem.objects.create(user=other_user, ingredient=honey, quantity='1 lb')
        r = auth_client.post(f'/pantry/{item.pk}/edit/', {'quantity': '99 lbs', 'notes': ''})
        assert r.status_code == 404
