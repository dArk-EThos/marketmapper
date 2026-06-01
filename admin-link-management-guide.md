# Market Mapper Admin Guide: Link Management

## Overview
The enhanced admin interface provides comprehensive tools for managing opportunity links, detecting dead URLs, and maintaining data quality.

## Accessing the Admin
- **URL**: https://test.casamaccoy.ca/admin/
- **Login**: Use your admin credentials
- **Navigate**: Go to **Opportunities → Opportunities**

## New Features

### 1. Link Status Column 
Shows at-a-glance URL status in the main opportunity list:
- **🔗 App URL | 🔗 Source** = Both URLs present
- **❌ App URL | 🔗 Source** = Application URL broken, source working
- **No URLs** = No links configured

### 2. Test Links Action (Bulk)
**How to use:**
1. Select opportunities (checkboxes on left)
2. Choose **"🔗 Test Links for Dead URLs"** from Actions dropdown
3. Click **"Go"**
4. Results appear as admin message
5. **Broken links automatically noted** in opportunity's Notes field

**What it checks:**
- HTTP status codes (404, 500, etc.)
- Connection failures (timeouts, DNS issues)
- Redirects (follows up to final destination)

### 3. Mark for Research Action
**Use when:** Links need human verification
1. Select opportunities needing research
2. Choose **"🔍 Mark as Needs Link Research"**
3. Automatically adds research flag to Notes
4. Sets confidence score to 3 (needs verification)

### 4. Enhanced Links & Source Tab
**In opportunity detail view:**
- **Application URL**: Direct vendor application page
- **Source URL**: Main event/organization website  
- **Link Status Display**: Real-time status indicators
- **Clear instructions**: "Use 'Test Links' action to verify"

## Link Management Workflow

### Weekly Link Maintenance
```
1. Go to Opportunities admin list
2. Sort by "Last Checked" (oldest first)
3. Select 10-20 older opportunities
4. Run "Test Links for Dead URLs" action
5. Review results and fix broken ones
```

### Fixing Dead Links
**When Test Links finds broken URLs:**

1. **Check the Notes field** - shows what failed
2. **Click opportunity name** to edit
3. **Go to Links & Source tab**
4. **Research new working URL** (use dead link workflow guide)
5. **Update Application URL or Source URL** 
6. **Clear old error notes** if desired
7. **Save**

### Research Process (from your methodology)
**For dead links:**
1. **Google search**: `"[Event Name] 2026" Manitoba vendor`
2. **Check municipal websites**: City/town event calendars
3. **Look for alternatives**: Chamber, Facebook, tourism sites
4. **Update URLs** with working alternatives
5. **Add research notes** for future reference

## Admin Interface Benefits

### Efficiency
- **Bulk testing** of multiple opportunities at once
- **Automatic flagging** of broken links  
- **Quick editing** of URLs without leaving admin
- **Visual indicators** show status at a glance

### Quality Control  
- **Systematic verification** prevents dead links from going live
- **Notes tracking** maintains research history
- **Confidence scoring** ensures quality standards
- **Human oversight** for nuanced decisions

### User Experience
- **No dead links** reach public users
- **Current information** maintains credibility
- **Working application URLs** help vendors apply successfully

## Example Admin Session

```
SCENARIO: Monthly link verification

1. Login to admin → Opportunities
2. Select 20 opportunities from list
3. Actions → "Test Links for Dead URLs" → Go
4. Review message: "5 working, 3 broken"
5. Filter by Notes containing "LINK CHECK"  
6. Edit each broken opportunity:
   - Research working alternative
   - Update Application URL
   - Clear error notes
   - Save
7. Re-test to confirm fixes
```

## Status Indicators Guide

| Display | Meaning | Action Needed |
|---------|---------|---------------|
| 🔗 App URL \| 🔗 Source | Both links working | None |
| ❌ App URL \| 🔗 Source | App link broken | Research new app URL |
| 🔗 App URL \| ❌ Source | Source link broken | Find new event website |
| No URLs | Missing links | Research and add URLs |

This admin interface gives you complete control over link quality while streamlining the process of maintaining current, working opportunities for Market Mapper users.