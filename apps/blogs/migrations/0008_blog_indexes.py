from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0007_alter_blog_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blog',
            options={'ordering': ['-date']},
        ),
        migrations.AlterField(
            model_name='blog',
            name='category',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='blog',
            name='date',
            field=models.DateField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='blog',
            name='language',
            field=models.CharField(choices=[('es', 'Español'), ('en', 'Inglés'), ('pt', 'Portugués')], db_index=True, default='es', max_length=2),
        ),
        migrations.AddIndex(
            model_name='blog',
            index=models.Index(fields=['-date'], name='blog_date_desc_idx'),
        ),
        migrations.AddIndex(
            model_name='blog',
            index=models.Index(fields=['language', '-date'], name='blog_lang_date_idx'),
        ),
        migrations.AddIndex(
            model_name='blog',
            index=models.Index(fields=['category', '-date'], name='blog_cat_date_idx'),
        ),
    ]


