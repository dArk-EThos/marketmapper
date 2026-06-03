# Step-by-step Canada expansion migration

from django.db import migrations, models
import django.db.models.deletion


def create_provinces(apps, schema_editor):
    """Create Canadian provinces and territories."""
    
    Province = apps.get_model('opportunities', 'Province')
    
    # Canadian provinces and territories with codes
    provinces_data = [
        ('Alberta', 'AB'),
        ('British Columbia', 'BC'),
        ('Manitoba', 'MB'),
        ('New Brunswick', 'NB'),
        ('Newfoundland and Labrador', 'NL'),
        ('Northwest Territories', 'NT'),
        ('Nova Scotia', 'NS'),
        ('Nunavut', 'NU'),
        ('Ontario', 'ON'),
        ('Prince Edward Island', 'PE'),
        ('Quebec', 'QC'),
        ('Saskatchewan', 'SK'),
        ('Yukon', 'YT'),
    ]
    
    # Create all provinces
    for name, code in provinces_data:
        slug = name.lower().replace(' ', '-').replace('&', 'and')
        Province.objects.get_or_create(
            code=code,
            defaults={'name': name, 'slug': slug}
        )
        print(f"Created province: {name} ({code})")


def update_regions(apps, schema_editor):
    """Update regions to belong to Manitoba."""
    
    Province = apps.get_model('opportunities', 'Province')
    Region = apps.get_model('opportunities', 'Region')
    
    # Get Manitoba province
    manitoba = Province.objects.get(code='MB')
    
    # Update existing regions to belong to Manitoba
    regions_updated = Region.objects.filter(province__isnull=True).update(province=manitoba)
    print(f"Updated {regions_updated} regions to belong to Manitoba")


def reverse_changes(apps, schema_editor):
    """Reverse the migration."""
    Province = apps.get_model('opportunities', 'Province')
    Province.objects.all().delete()


class Migration(migrations.Migration):
    
    dependencies = [
        ('opportunities', '0006_add_guidelines_url'),
    ]
    
    operations = [
        # First create Province model
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=2, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        
        # Add province FK to Region (nullable initially)
        migrations.AddField(
            model_name='region',
            name='province',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='regions', to='opportunities.province'),
        ),
        
        # Create provinces
        migrations.RunPython(create_provinces, reverse_changes),
        
        # Update regions to belong to Manitoba
        migrations.RunPython(update_regions, reverse_changes),
        
        # Make Region.province required after data migration
        migrations.AlterField(
            model_name='region',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='regions', to='opportunities.province'),
        ),
        
        # Update Region unique constraints
        migrations.AlterUniqueTogether(
            name='region',
            unique_together={('province', 'slug'), ('province', 'name')},
        ),
    ]
