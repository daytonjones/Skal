from django.db import migrations, models


def approve_existing_users(apps, schema_editor):
    # Everyone who existed before this feature is auto-approved.
    User = apps.get_model('accounts', 'User')
    User.objects.all().update(is_approved=True)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_user_gravatar_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(approve_existing_users, migrations.RunPython.noop),
    ]
