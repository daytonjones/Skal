from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, RecipeIngredient, Ingredient


class RecipeForm(forms.ModelForm):
    honey = forms.CharField(
        label='Honey',
        widget=forms.TextInput(attrs={'list': 'honey-list'}),
        max_length=100
    )
    honey_quantity = forms.DecimalField(
        label='Honey Quantity (lbs)',
        max_digits=5,
        decimal_places=1,
        min_value=0.1,
        help_text='Enter weight in pounds'
    )
    water = forms.CharField(
        label='Water',
        widget=forms.TextInput(attrs={'list': 'water-list'}),
        max_length=100
    )
    water_quantity = forms.DecimalField(
        label='Water Quantity (gal)',
        max_digits=5,
        decimal_places=1,
        min_value=0.1,
        help_text='Enter volume in gallons'
    )
    yeast = forms.CharField(
        label='Yeast',
        widget=forms.TextInput(attrs={'list': 'yeast-list'}),
        max_length=100
    )
    yeast_quantity = forms.CharField(
        label='Yeast Quantity',
        max_length=50,
        help_text='e.g. “1 packet”'
    )
    is_public = forms.BooleanField(
        required=False,
        label='Public',
        help_text='Allow others to view this recipe'
    )

    class Meta:
        model = Recipe
        fields = [
            'name',
            'batch_size',
            'instructions',
            'honey',
            'honey_quantity',
            'water',
            'water_quantity',
            'yeast',
            'yeast_quantity',
            'is_public',
        ]


class RecipeIngredientForm(forms.ModelForm):
    ingredient_name = forms.CharField(
        label='Ingredient',
        widget=forms.TextInput(attrs={'list': 'ingredient-list'}),
        max_length=100
    )

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient_name', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # on edit, prefill the ingredient_name
        if self.instance.pk and self.instance.ingredient:
            self.fields['ingredient_name'].initial = self.instance.ingredient.name

    def save(self, commit=True):
        name = self.cleaned_data.get('ingredient_name', '').strip()
        try:
            ingredient = Ingredient.objects.get(name__iexact=name)
        except Ingredient.DoesNotExist:
            ingredient = Ingredient.objects.create(name=name, type=Ingredient.TYPE_ADDITIVE)
        except Ingredient.MultipleObjectsReturned:
            ingredient = Ingredient.objects.filter(name__iexact=name).first()
        self.instance.ingredient = ingredient
        return super().save(commit=commit)


RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=1,
    can_delete=True,
)

