from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='update',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='updates/covers/'),
        ),
    ]
