# This file will be to specify the search form fields

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Recipe
from django.utils.safestring import mark_safe

class SignupForm(UserCreationForm):
  """
  Custom signup form extending Django's built-in UserCreationForm.
  Adds optional fields for email and first name.
  """

  username = forms.CharField(
    max_length=50,
    help_text="50 characters or fewer. Letters, digits, and @/./+/- only."
  )

  password1 = forms.CharField(
    widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    label="Password",
    help_text=mark_safe(
      "Your password must contain at least 8 characters.<br>"
      "Your password must be alphanumeric."
    )
  )

  password2 = forms.CharField(
    widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    label="Confirm password",
    help_text="Enter the same password again for verification."
  )

  email = forms.CharField(
    required=False,
    help_text="Optional. Provide your email address if you'd like."
  )

  first_name = forms.CharField(
    required=False,
    help_text="Optional. Provide your first name if you'd like."
  )

  class Meta:
    """
    Defines metadata for the SignupForm.
    Specifies the model and fields to include in the form.
    """
    model = User
    fields = ['username', 'password1', 'password2', 'email', 'first_name']

CHART_CHOICES = (
  ('', 'Select Chart Type...'),
  ('#1', 'Bar Chart'), # When user selects "Bar Chart", it is stored as "#1"
  ('#2', 'Pie Chart'),
  ('#3', 'Line Chart')
)

# Specify difficulty level choices as a tuple
DIFFICULTY_CHOICES = (
  ('', 'Select Difficulty...'),
  ('Easy', 'Easy'), # When user selects "Easy", it is stored as "Easy"
  ('Medium', 'Medium'),
  ('Intermediate', 'Intermediate'),
  ('Hard', 'Hard')
)

# Define class-based Form imported from Django forms
class RecipeSearchForm(forms.Form):
  # Allows users to search by recipe name
  recipe_name = forms.CharField(
    max_length=120,
    required=False,
    label='Recipe Name',
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter a recipe name...'
    })
  )
  # Allows users to search by ingredient
  ingredient = forms.CharField(
    max_length=120,
    required=False,
    label='Ingredient',
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter an ingredient...'
    })
  )
  # Dropdown menu to filter recipes by difficulty level
  difficulty = forms.ChoiceField(
    choices=DIFFICULTY_CHOICES,
    required=False,
    label='Difficulty Level',
    widget=forms.Select(attrs={
      'class': 'form-select'
    })
  )
  # Dropdown menu to select chart type for data visualization
  chart_type = forms.ChoiceField(
    choices=CHART_CHOICES,
    required=False,
    label='Chart Type',
    widget=forms.Select(attrs={
      'class': 'form-select'
    })
  )