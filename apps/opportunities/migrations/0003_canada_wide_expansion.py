# Generated migration for Canada-wide expansion

from django.db import migrations, models
import django.db.models.deletion


def create_provinces_and_regions(apps, schema_editor):
    """Create Canadian provinces and reorganize existing Manitoba regions."""
    
    Province = apps.get_model('opportunities', 'Province')
    Region = apps.get_model('opportunities', 'Region')
    Opportunity = apps.get_model('opportunities', 'Opportunity')
    
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
    province_objects = {}
    for name, code in provinces_data:
        slug = name.lower().replace(' ', '-').replace('&', 'and')
        province = Province.objects.create(name=name, code=code, slug=slug)
        province_objects[code] = province
        print(f"Created province: {name} ({code})")
    
    # Get Manitoba province for existing regions
    manitoba = province_objects['MB']
    
    # Update existing regions to belong to Manitoba
    existing_regions = Region.objects.all()
    for region in existing_regions:
        # Add province field to existing regions
        region.province = manitoba
        region.save()
        print(f"Updated region: {region.name} -> {manitoba.name}")
    
    # Update existing opportunities
    opportunities = Opportunity.objects.all()
    
    for opp in opportunities:
        # Map existing province text to Province object
        if hasattr(opp, 'province'):  # Check if it's still a CharField
            province_text = getattr(opp, 'province', 'Manitoba')
            
            # Try to match existing province text to a Province object
            if province_text in ['Manitoba', 'MB']:
                opp.province = manitoba
            elif province_text in ['Alberta', 'AB']:
                opp.province = province_objects['AB']
            elif province_text in ['British Columbia', 'BC']:
                opp.province = province_objects['BC']
            elif province_text in ['Ontario', 'ON']:
                opp.province = province_objects['ON']
            else:
                # Default to Manitoba for any unclear cases
                opp.province = manitoba
            
            opp.save()
            print(f"Updated opportunity: {opp.opportunity_name} -> {opp.province.name}")
    
    print(f"Migration completed: {len(provinces_data)} provinces, {existing_regions.count()} regions, {opportunities.count()} opportunities")


def reverse_provinces_and_regions(apps, schema_editor):
    """Reverse the migration."""
    Province = apps.get_model('opportunities', 'Province')
    Opportunity = apps.get_model('opportunities', 'Opportunity')
    
    # Set province field back to text for all opportunities
    for opp in Opportunity.objects.all():
        if opp.province:
            opp.province_text = opp.province.name
            opp.save()
    
    # Delete all provinces (regions will be updated to remove province FK)
    Province.objects.all().delete()


class Migration(migrations.Migration):
    
    dependencies = [
        ('opportunities', '0001_initial'),  # Update this to your latest migration
    ]
    
    operations = [
        # Add Province model
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
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='regions', to='opportunities.province'),
        ),
        
        # Add province FK to Opportunity (nullable initially) 
        migrations.AddField(
            model_name='opportunity',
            name='province_new',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to='opportunities.province'),
        ),
        
        # Add submission tracking fields to Opportunity
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
        
        # Run data migration
        migrations.RunPython(create_provinces_and_regions, reverse_provinces_and_regions),
        
        # Make province required and remove old province field
        migrations.AlterField(
            model_name='opportunity',
            name='province_new',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to='opportunities.province'),
        ),
        
        migrations.RemoveField(
            model_name='opportunity',
            name='province',
        ),
        
        migrations.RenameField(
            model_name='opportunity',
            old_name='province_new',
            new_name='province',
        ),
        
        # Make Region.province required
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
        
        # Add indexes
        migrations.AddIndex(
            model_name='opportunity',
            index=models.Index(fields=['province'], name='idx_province'),
        ),
        migrations.AddIndex(
            model_name='opportunity',
            index=models.Index(fields=['verification_status'], name='idx_verification_status'),
        ),
        
        # Create OpportunitySubmission model
        migrations.CreateModel(
            name='OpportunitySubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('submitter_name', models.CharField(max_length=200)),
                ('submitter_email', models.EmailField(max_length=254)),
                ('submitter_organization', models.CharField(blank=True, help_text='Organization name if submitting on behalf of one', max_length=200)),
                ('opportunity_name', models.CharField(max_length=255)),
                ('province_name', models.CharField(help_text='Province/territory name', max_length=100)),
                ('region_name', models.CharField(blank=True, help_text='Region within province (optional)', max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('venue', models.CharField(blank=True, max_length=200)),
                ('opportunity_type', models.CharField(choices=[('farmers_market', 'Farmers Market'), ('craft_fair', 'Craft Fair'), ('food_festival', 'Food Festival'), ('night_market', 'Night Market'), ('pop_up', 'Pop-Up'), ('holiday_market', 'Holiday Market'), ('exhibition', 'Exhibition'), ('community_event', 'Community Event'), ('retail_opportunity', 'Retail Opportunity'), ('other', 'Other')], max_length=50)),
                ('event_date_text', models.CharField(help_text="When does this event occur? (e.g., 'Every Saturday', 'June 15-17, 2026')", max_length=200)),
                ('application_deadline_text', models.CharField(blank=True, help_text='When is the application deadline?', max_length=255)),
                ('application_url', models.URLField(blank=True, help_text='Where can vendors apply?', max_length=500)),
                ('source_url', models.URLField(help_text='Link to event information', max_length=500)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('organizer_name', models.CharField(blank=True, max_length=200)),
                ('vendor_fee', models.CharField(blank=True, help_text="Cost to participate (e.g., '$50', 'Free', 'Percentage of sales')", max_length=255)),
                ('vendor_categories_text', models.CharField(blank=True, help_text='What types of vendors are they looking for?', max_length=255)),
                ('additional_notes', models.TextField(blank=True, help_text='Any other details about this opportunity')),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved (Converted to Opportunity)'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('admin_notes', models.TextField(blank=True, help_text='Internal notes for admin review')),
                ('reviewed_by', models.CharField(blank=True, help_text='Admin who reviewed this submission', max_length=100)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('converted_opportunity', models.ForeignKey(blank=True, help_text='The opportunity created from this submission', null=True, on_delete=django.db.models.deletion.SET_NULL, to='opportunities.opportunity')),
            ],
            options={
                'verbose_name': 'Opportunity Submission',
                'verbose_name_plural': 'Opportunity Submissions',
                'ordering': ['-submitted_at'],
            },
        ),
    ]
