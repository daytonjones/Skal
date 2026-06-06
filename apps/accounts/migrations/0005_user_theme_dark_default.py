from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='theme',
            field=models.CharField(
                choices=[('light', 'Light'), ('dark', 'Dark')],
                default='dark',
                max_length=20,
            ),
        ),
    ]
