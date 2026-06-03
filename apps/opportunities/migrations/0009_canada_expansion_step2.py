# Opportunity model Canada expansion

from django.db import migrations, models
import django.db.models.deletion


def update_opportunity_provinces(apps, schema_editor):
    """Update opportunities to use Province FK."""
    
    Province = apps.get_model('opportunities', 'Province')
    Opportunity = apps.get_model('opportunities', 'Opportunity')
    
    # Get Manitoba province
    manitoba = Province.objects.get(code='MB')
    
    # Update all opportunities to use Manitoba (since they're all currently Manitoba-based)
    opportunities = Opportunity.objects.all()
    
    for opp in opportunities:
        opp.province_fk = manitoba
        opp.save(update_fields=['province_fk'])
        
    print(f"Updated {opportunities.count()} opportunities to use Province FK")


def reverse_opportunity_changes(apps, schema_editor):
    """Reverse the changes."""
    pass  # Nothing to reverse since we're removing the old field


class Migration(migrations.Migration):
    
    dependencies = [
        ('opportunities', '0008_canada_expansion_step1'),
    ]
    
    operations = [
        # Add new province FK field (nullable initially)
        migrations.AddField(
            model_name='opportunity',
            name='province_fk',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to='opportunities.province'),
        ),
        
        # Run data migration
        migrations.RunPython(update_opportunity_provinces, reverse_opportunity_changes),
        
        # Make province FK required
        migrations.AlterField(
            model_name='opportunity',
            name='province_fk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to='opportunities.province'),
        ),
        
        # Remove old province CharField
        migrations.RemoveField(
            model_name='opportunity',
            name='province',
        ),
        
        # Rename province_fk to province
        migrations.RenameField(
            model_name='opportunity',
            old_name='province_fk',
            new_name='province',
        ),
        
        # Add submission tracking fields
        migrations.AddField(
            model_name='opportunity',
            name='submitter_name',
            field=models.CharField(blank=True, help_text='Name of person who submitted this opportunity', max_length=200),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='submitter_email',
            field=models.EmailField(blank=True, help_text='Email of person who submitted this opportunity', max_length=254),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='submission_notes',
            field=models.TextField(blank=True, help_text='Internal notes about this submission'),
        ),
        
        # Update SOURCE_TYPES to include user_submission
        migrations.AlterField(
            model_name='opportunity',
            name='source_type',
            field=models.CharField(choices=[('official', 'Official Website'), ('organizer', 'Organizer Direct'), ('municipal', 'Municipal/Government'), ('social_organizer', 'Social Media (Organizer)'), ('social_repost', 'Social Media (Repost)'), ('community', 'Community Tip'), ('user_submission', 'User Submission')], max_length=30),
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='opportunity',
            index=models.Index(fields=['province'], name='idx_province'),
        ),
    ]