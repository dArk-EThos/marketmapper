# Dead Link Resolution Workflow for Market Mapper Admins

## Overview
Automated link checking identifies broken URLs, but human research is needed to find working alternatives. This workflow provides a systematic approach for admins to resolve dead links efficiently.

## Admin Dashboard Integration

### 1. Dead Link Detection
- **Automated Check**: Run link verification scripts monthly
- **Admin Flag**: Mark opportunities as "link-needs-verification" 
- **Priority Queue**: Show dead link opportunities in admin dashboard
- **Batch Processing**: Handle multiple dead links in one session

### 2. Research Methodology (Your Proven Approach)

#### Step 1: Identify the Issue
```
❌ Dead Link Example: https://neepawafair.com/ (404/Connection Failed)
```

#### Step 2: Google Search Strategy
**Search Terms**: `"[Event Name] 2026" + "Manitoba" + "vendor" OR "craft fair"`
```
Example: "Neepawa fair 2026" Manitoba
```

#### Step 3: Alternative Source Hierarchy
1. **Municipal Website**: City/town official events calendar
2. **Chamber of Commerce**: Local business association events  
3. **Facebook/Social**: Official event pages
4. **Local News**: Recent articles about the event
5. **Tourism Sites**: Regional tourism event listings

#### Step 4: Information Verification
Look for these key details:
- ✅ **Current year dates** (2026)
- ✅ **Venue confirmation** 
- ✅ **Contact method** (even if indirect)
- ✅ **Event type match** (craft fair, farmers market, etc.)
- ✅ **Annual event confirmation** (not one-time)

## Admin Interface Workflow

### Research Results Form
```
Dead Link: [Original broken URL]
Event Status: 
□ Event still exists - found working info
□ Event cancelled/discontinued  
□ Event moved/renamed
□ Need more research

If Event Exists:
New Source URL: [Working website/page]
New Application URL: [If vendor page found]
Updated Event Dates: [From research]
Contact Method: [How vendors should apply]
Research Notes: [Your findings summary]
Confidence Score: [1-5, where 4-5 = publishable]
```

### Example Resolution (Neepawa Case)
```
✅ RESOLVED
Dead Link: https://neepawafair.com/
Research Found: Neepawa & District Craft Fair
New Source: https://www.neepawaonline.com/events  
Event Dates: June 6-7, 2026, 10am-5pm
Venue: Yellowhead Centre
Contact: Via Neepawa Online events page
Notes: Local artisans and crafters. Free admission.
Confidence: 4/5 (Official municipal calendar)
```

## Admin Actions After Research

### 1. Update Database Entry
- Replace dead URLs with working alternatives
- Update event information with current data
- Add research notes for future reference
- Set confidence score based on source quality

### 2. Create Contact Strategy
When no direct vendor application exists:
- **Municipal Contact**: "Contact [City] via events page"
- **Social Media**: "Follow [Event Facebook] for vendor updates"  
- **Chamber Contact**: "Contact [Local Chamber] for vendor info"
- **Phone/Email**: Include if found during research

### 3. Quality Assurance
- Mark as "verified-[date]" after fixing
- Schedule re-verification in 6 months
- Flag for removal if event truly discontinued

## Batch Processing Tips

### Efficient Research Session
1. **Prep**: Queue 5-10 dead link opportunities
2. **Research**: Use multiple browser tabs for parallel searching
3. **Document**: Fill out research form for each
4. **Update**: Batch update all findings in admin
5. **Verify**: Quick test of new URLs before saving

### Common Resolution Patterns
- **Fairs/Festivals**: Usually move to municipal websites
- **Farmers Markets**: Often on Facebook or chamber sites
- **Craft Shows**: May be managed by community centers
- **Trade Shows**: Check industry association sites

## Success Metrics
- **Response Time**: Resolve dead links within 1 week of detection
- **Success Rate**: 80%+ of researched events should be recoverable
- **User Experience**: No dead links visible to public users
- **Credibility**: All published information matches official sources

## Escalation Path
If research doesn't find current information:
1. **Mark as "research-needed"** - hide from public but keep in admin
2. **Set reminder** to check again in 3 months (events may update)
3. **Consider removal** only after 2 failed research attempts
4. **Document reasoning** for future reference

This human-in-the-loop approach maintains Market Mapper's credibility while ensuring comprehensive coverage of Manitoba vendor opportunities.