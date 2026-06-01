#!/bin/bash
# Market Mapper 2026 Date Update Script
# Updates stale 2025 dates with current 2026 information

echo "=== MARKET MAPPER 2026 DATE UPDATE ==="
echo "Updating opportunities with stale 2025 dates to current 2026 dates"

cd /opt/marketmapper
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.production

# Major annual festivals - update to 2026 dates
echo "Updating major annual festivals..."

# Provincial Exhibition (typically early June)
python manage.py shell -c "
from apps.opportunities.models import Opportunity
from datetime import date
prov = Opportunity.objects.get(id=38)
prov.event_date = date(2026, 6, 3)
prov.event_date_end = date(2026, 6, 8) 
prov.event_date_text = 'June 3-8, 2026 (6 days)'
prov.notes = 'Updated to 2026 dates - verify exact dates closer to event'
prov.save()
print('✅ Updated Provincial Exhibition')
"

# Red River Exhibition (typically mid-June) 
python manage.py shell -c "
from apps.opportunities.models import Opportunity
from datetime import date
red = Opportunity.objects.get(id=13)
red.event_date = date(2026, 6, 12)
red.event_date_end = date(2026, 6, 21)
red.event_date_text = 'June 12-21, 2026 (10 days)'
red.notes = 'Updated to 2026 dates - verify exact dates closer to event'
red.save()
print('✅ Updated Red River Exhibition')
"

# Winnipeg Folk Festival (typically mid-July)
python manage.py shell -c "
from apps.opportunities.models import Opportunity
from datetime import date
folk = Opportunity.objects.get(id=17)
folk.event_date = date(2026, 7, 9)
folk.event_date_end = date(2026, 7, 12)
folk.event_date_text = 'July 9-12, 2026'
folk.notes = 'Updated to 2026 dates - verify exact dates closer to event'
folk.save()
print('✅ Updated Folk Festival')
"

# Folklorama (typically first 2 weeks of August)
python manage.py shell -c "
from apps.opportunities.models import Opportunity
from datetime import date
folklorama = Opportunity.objects.get(id=14)
folklorama.event_date = date(2026, 8, 2)
folklorama.event_date_end = date(2026, 8, 15)
folklorama.event_date_text = 'August 2-15, 2026 (2 weeks)'
folklorama.notes = 'Updated to 2026 dates - verify exact dates closer to event'
folklorama.save()
print('✅ Updated Folklorama')
"

# Icelandic Festival (August long weekend)
python manage.py shell -c "
from apps.opportunities.models import Opportunity
from datetime import date
icelandic = Opportunity.objects.get(id=18)
icelandic.event_date = date(2026, 8, 1)
icelandic.event_date_end = date(2026, 8, 4)
icelandic.event_date_text = 'August 1-4, 2026 (August long weekend)'
icelandic.notes = 'Updated to 2026 dates - August long weekend'
icelandic.save()
print('✅ Updated Icelandic Festival')
"

echo "✅ Major festivals updated with 2026 dates"
echo "⚠️  NOTE: These are projected dates based on historical patterns"
echo "🔍 VERIFY: Check official websites closer to events for exact dates"