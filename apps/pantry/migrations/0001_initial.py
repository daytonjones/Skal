from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipes', '0006_seed_recipes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PantryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.CharField(blank=True, default='', max_length=100)),
                ('notes', models.TextField(blank=True, default='')),
                ('ingredient', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='pantry_items',
                    to='recipes.ingredient',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='pantry_items',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['ingredient__type', 'ingredient__name'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='pantryitem',
            unique_together={('user', 'ingredient')},
        ),
    ]
