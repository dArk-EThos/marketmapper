# Django Management Command: Update Stale Dates
# Place in: apps/opportunities/management/commands/update_stale_dates.py

from django.core.management.base import BaseCommand
from apps.opportunities.models import Opportunity
from datetime import date
import re

class Command(BaseCommand):
    help = 'Update opportunities with stale 2025 dates to current year'
    
    def handle(self, *args, **options):
        self.stdout.write("=== UPDATING STALE 2025 DATES ===")
        
        # Find all opportunities with 2025 references
        stale_ops = []
        for opp in Opportunity.objects.all():
            has_2025 = False
            
            if opp.event_date_text and '2025' in str(opp.event_date_text):
                has_2025 = True
            if opp.event_date and '2025' in str(opp.event_date):
                has_2025 = True
            if opp.application_deadline and '2025' in str(opp.application_deadline):
                has_2025 = True
                
            if has_2025:
                stale_ops.append(opp)
        
        self.stdout.write(f"Found {len(stale_ops)} opportunities with 2025 references")
        
        # Update major annual festivals
        festival_updates = {
            'Provincial Exhibition': {
                'event_text': 'June 2026 (exact dates TBD - check official website)',
                'notes': 'Annual summer fair - typically early June'
            },
            'Folk Festival': {
                'event_text': 'July 2026 (exact dates TBD - check official website)', 
                'notes': 'Annual folk festival - typically mid-July'
            },
            'Countryfest': {
                'event_text': 'June 25-28, 2026',
                'notes': 'Verified 2026 dates from official website'
            },
            'Red River': {
                'event_text': 'June 2026 (exact dates TBD - check official website)',
                'notes': 'Annual exhibition - typically mid-June'
            },
            'Folklorama': {
                'event_text': 'August 2026 (exact dates TBD - check official website)',
                'notes': 'Annual multicultural festival - typically first 2 weeks of August'
            },
            'Icelandic Festival': {
                'event_text': 'August 2026 long weekend (exact dates TBD)',
                'notes': 'Annual festival - typically August long weekend'
            }
        }
        
        updated_count = 0
        for opp in stale_ops:
            # Find matching festival
            updated = False
            for fest_name, updates in festival_updates.items():
                if fest_name.lower() in opp.opportunity_name.lower():
                    opp.event_date_text = updates['event_text']
                    opp.notes = updates['notes']
                    opp.save()
                    self.stdout.write(f"✅ Updated {opp.opportunity_name}")
                    updated = True
                    updated_count += 1
                    break
            
            # Generic update for others
            if not updated and opp.event_date_text:
                # Replace 2025 with 2026 in text
                new_text = re.sub(r'2025', '2026 (verify dates)', opp.event_date_text)
                opp.event_date_text = new_text
                opp.notes = 'Updated year reference - verify exact 2026 dates on official website'
                opp.save()
                self.stdout.write(f"⚠️  Generic update: {opp.opportunity_name}")
                updated_count += 1
        
        self.stdout.write(f"\n✅ Updated {updated_count} opportunities")
        self.stdout.write("🔍 IMPORTANT: Verify exact dates on official websites before publishing")
        self.stdout.write("📅 Some dates are projected based on historical patterns")