# 🗺️ Tour Planner Agent Guide

## Overview

The Tour Planner Agent is an example agent that demonstrates:
- **Planning**: Creates detailed tour itineraries
- **External Actions**: Books events to Google Calendar
- **User Confirmation**: Asks for approval before executing external actions
- **Dashboard Integration**: Shows plans and notifications in the UI

---

## 🚀 Features

### 1. Tour Planning
- Researches destination
- Creates detailed day itinerary
- Generates summary
- Organizes activities by time slots

### 2. Google Calendar Integration
- Creates calendar events for:
  - Morning activities (9 AM - 12 PM)
  - Afternoon activities (12 PM - 5 PM)
  - Evening activities (5 PM - 9 PM)
- Requires user confirmation before booking

### 3. Dashboard Display
- Shows complete tour plan
- Displays itinerary
- Shows calendar event notifications
- Provides confirmation buttons

---

## 📋 Usage

### Input Parameters

1. **Destination** (string)
   - Example: "Paris", "Tokyo", "New York"

2. **Date** (string)
   - Format: "YYYY-MM-DD" or "2024-12-25"
   - Example: "2024-12-25"

### Example Input

```
Destination: Paris
Date: 2024-12-25
```

---

## 📊 Output Structure

### Main Outputs

1. **itinerary** - Complete day tour plan with:
   - Morning activities (9 AM - 12 PM)
   - Afternoon activities (12 PM - 5 PM)
   - Evening activities (5 PM - 9 PM)
   - Recommended restaurants
   - Travel tips

2. **tour_summary** - Brief 2-3 sentence summary

3. **final_plan** - Aggregated plan with all details

### Calendar Events

1. **morning_event** - Morning tour activities
2. **afternoon_event** - Afternoon tour activities
3. **evening_event** - Evening tour activities

Each event includes:
- Title
- Description
- Start/End time
- Location
- Status (pending_confirmation)

### Notifications

The agent creates notifications for:
- Calendar events ready for booking
- Actions requiring confirmation

---

## 🎯 Dashboard Features

### Notifications Section

When you run the Tour Planner, the dashboard shows:

1. **🔔 Notifications & External Actions**
   - Lists all calendar events
   - Shows event details
   - Provides confirmation buttons

2. **Confirmation Buttons**
   - **✅ Confirm & Execute** - Approves and executes the action
   - **❌ Cancel** - Cancels the action

### Output Display

1. **📋 Key Results Tab**
   - Complete Plan
   - Tour Itinerary
   - Summary

2. **🔍 All State Tab**
   - All state variables
   - Calendar events
   - Notifications

---

## 🔧 How It Works

### Workflow Steps

1. **Parse Input** - Extracts destination and date
2. **Research** - Searches for destination information
3. **Create Itinerary** - LLM generates detailed plan
4. **Create Summary** - LLM generates brief summary
5. **Create Calendar Events** - Creates 3 calendar events
6. **Aggregate** - Combines everything into final plan
7. **Output** - Formats and displays results

### External Actions

The `google_calendar` node type:
- Creates event data
- Stores in state
- Creates notification
- Sets `requires_confirmation: true`
- Waits for user approval

---

## 💡 Customization

### Modify Itinerary Times

Edit `tour_planner_agent_workflow.yaml`:

```yaml
- id: "calendar_morning"
  type: "google_calendar"
  config:
    start_date: "{tour_date} 09:00"  # Change start time
    end_date: "{tour_date} 12:00"     # Change end time
```

### Add More Calendar Events

Add new calendar nodes:

```yaml
- id: "calendar_lunch"
  type: "google_calendar"
  config:
    event_title: "Lunch at {restaurant}"
    start_date: "{tour_date} 13:00"
    end_date: "{tour_date} 14:00"
    require_confirmation: true
```

### Change Event Details

Modify event configuration:

```yaml
config:
  event_title: "Custom Title: {destination}"
  event_description: "Custom description with {variables}"
  location: "{custom_location}"
```

---

## 🎨 Dashboard Integration

### Generic Support

The dashboard automatically:
- ✅ Detects external actions
- ✅ Shows notifications
- ✅ Provides confirmation UI
- ✅ Works with any agent using external nodes

### For Other Agents

Any agent can use external actions:

```yaml
- id: "send_email"
  type: "external_action"
  config:
    action_type: "email"
    action_description: "Send email to {recipient}"
    action_data:
      to: "{recipient}"
      subject: "{subject}"
      body: "{body}"
    require_confirmation: true
```

The dashboard will automatically show it!

---

## 🔐 Google Calendar Integration

### Current Implementation

The current implementation:
- Creates event data structure
- Stores in state
- Shows in dashboard
- Requires user confirmation

### Future Enhancement

To actually book to Google Calendar:

1. **Install Google API Client:**
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. **Get OAuth Credentials:**
   - Create project in Google Cloud Console
   - Enable Calendar API
   - Create OAuth 2.0 credentials

3. **Update GoogleCalendarNode:**
   - Add OAuth flow
   - Implement actual API calls
   - Handle authentication

---

## 📝 Example Output

### Itinerary
```
Morning Activities (9 AM - 12 PM):
- Visit Eiffel Tower
- Walk along Seine River
- Coffee at local café

Afternoon Activities (12 PM - 5 PM):
- Louvre Museum tour
- Lunch at French restaurant
- Shopping on Champs-Élysées

Evening Activities (5 PM - 9 PM):
- Dinner cruise on Seine
- Visit Montmartre
- Enjoy nightlife
```

### Calendar Events
- 📅 Tour: Paris - Morning Activities (2024-12-25 09:00 - 12:00)
- 📅 Tour: Paris - Afternoon Activities (2024-12-25 12:00 - 17:00)
- 📅 Tour: Paris - Evening Activities (2024-12-25 17:00 - 21:00)

---

## 🎓 Learning Points

This agent demonstrates:
1. **Multi-step planning** - Research → Plan → Summary
2. **External integrations** - Google Calendar
3. **User confirmation** - Approval workflow
4. **Dashboard integration** - Generic UI support
5. **State management** - Passing data between nodes

---

**Enjoy planning your tours! 🗺️✈️**

