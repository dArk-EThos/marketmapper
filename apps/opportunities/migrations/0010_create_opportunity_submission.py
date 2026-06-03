# Create OpportunitySubmission model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    
    dependencies = [
        ('opportunities', '0009_canada_expansion_step2'),
    ]
    
    operations = [
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