from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0002_update_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='update',
            name='author_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='update',
            name='cover_image_caption',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
