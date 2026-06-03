from django import forms
from django.core.exceptions import ValidationError
from .models import OpportunitySubmission, Opportunity


class OpportunitySubmissionForm(forms.ModelForm):
    """Form for users to submit new opportunities."""
    
    # Override some fields with better widgets and help text
    submitter_name = forms.CharField(
        max_length=200,
        label="Your Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name'
        })
    )
    
    submitter_email = forms.EmailField(
        label="Your Email",
        help_text="We'll only use this to contact you about your submission.",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    
    submitter_organization = forms.CharField(
        max_length=200,
        required=False,
        label="Organization (Optional)",
        help_text="If you're submitting on behalf of an organization.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Organization name'
        })
    )
    
    opportunity_name = forms.CharField(
        max_length=255,
        label="Event/Market Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Downtown Farmers Market'
        })
    )
    
    opportunity_type = forms.ChoiceField(
        choices=Opportunity.OPPORTUNITY_TYPES,
        label="Event Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    province_name = forms.CharField(
        max_length=100,
        label="Province/Territory",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Alberta, British Columbia'
        })
    )
    
    region_name = forms.CharField(
        max_length=100,
        required=False,
        label="Region (Optional)",
        help_text="Regional area within the province, if applicable.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Lower Mainland, Central Alberta'
        })
    )
    
    city = forms.CharField(
        max_length=100,
        label="City/Town",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Calgary, Vancouver'
        })
    )
    
    venue = forms.CharField(
        max_length=200,
        required=False,
        label="Venue/Location (Optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Community Center, City Park'
        })
    )
    
    event_date_text = forms.CharField(
        max_length=200,
        label="When does this event happen?",
        help_text="Be as specific as possible (dates, recurring schedule, etc.)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "e.g., 'Every Saturday 9am-3pm' or 'June 15-17, 2026'"
        })
    )
    
    application_deadline_text = forms.CharField(
        max_length=255,
        required=False,
        label="Application Deadline (Optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "e.g., 'March 1st' or 'Rolling basis'"
        })
    )
    
    application_url = forms.URLField(
        max_length=500,
        required=False,
        label="Application Link (Optional)",
        help_text="Where can vendors apply?",
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/vendor-application'
        })
    )
    
    source_url = forms.URLField(
        max_length=500,
        label="Event Information Link",
        help_text="Link to official event page, social media, or other source.",
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/event-info'
        })
    )
    
    contact_email = forms.EmailField(
        required=False,
        label="Organizer Email (Optional)",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'organizer@example.com'
        })
    )
    
    organizer_name = forms.CharField(
        max_length=200,
        required=False,
        label="Organizer Name (Optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Event organizer or organization'
        })
    )
    
    vendor_fee = forms.CharField(
        max_length=255,
        required=False,
        label="Vendor Fee (Optional)",
        help_text="Cost to participate (e.g., '$50', 'Free', 'Percentage of sales')",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "e.g., '$75', 'Free', '10% of sales'"
        })
    )
    
    vendor_categories_text = forms.CharField(
        max_length=255,
        required=False,
        label="Vendor Categories (Optional)",
        help_text="What types of vendors are they looking for?",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Food, Crafts, Art, Farm products'
        })
    )
    
    additional_notes = forms.CharField(
        required=False,
        label="Additional Notes (Optional)",
        help_text="Any other details about this opportunity that would be helpful to vendors.",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Additional details, special requirements, etc.'
        })
    )
    
    # Honeypot field for spam protection
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="Website"  # This should not be visible to humans
    )
    
    class Meta:
        model = OpportunitySubmission
        fields = [
            'submitter_name', 'submitter_email', 'submitter_organization',
            'opportunity_name', 'opportunity_type', 'province_name', 'region_name',
            'city', 'venue', 'event_date_text', 'application_deadline_text',
            'application_url', 'source_url', 'contact_email', 'organizer_name',
            'vendor_fee', 'vendor_categories_text', 'additional_notes'
        ]
    
    def clean_website(self):
        """Honeypot spam protection."""
        website = self.cleaned_data.get('website')
        if website:
            raise ValidationError("Spam detected.")
        return website
    
    def clean_source_url(self):
        """Validate source URL is accessible."""
        url = self.cleaned_data.get('source_url')
        if url:
            # Basic URL validation (Django's URLField already handles format)
            # Could add more sophisticated checking here if needed
            pass
        return url
    
    def clean(self):
        """Additional form validation."""
        cleaned_data = super().clean()
        
        # Ensure at least one contact method
        application_url = cleaned_data.get('application_url')
        contact_email = cleaned_data.get('contact_email')
        
        if not application_url and not contact_email:
            raise ValidationError(
                "Please provide either an application link or organizer email so vendors know how to get involved."
            )
        
        return cleaned_data


class OpportunitySubmissionAdminForm(forms.ModelForm):
    """Admin form for reviewing submissions and converting to opportunities."""
    
    class Meta:
        model = OpportunitySubmission
        fields = '__all__'
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 4}),
            'additional_notes': forms.Textarea(attrs={'rows': 4}),
        }