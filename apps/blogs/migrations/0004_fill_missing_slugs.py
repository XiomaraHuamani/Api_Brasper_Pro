from django.db import migrations
from django.utils.text import slugify

def generate_slugs(apps, schema_editor):
    Blog = apps.get_model('blogs', 'Blog')
    for blog in Blog.objects.filter(slug__isnull=True):
        blog.slug = slugify(blog.title) or f'blog-{blog.id}'
        blog.save()

class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0003_alter_blog_slug'),  # Django reemplazará esto con la última migración real automáticamente
    ]

    operations = [
        migrations.RunPython(generate_slugs),
    ]
