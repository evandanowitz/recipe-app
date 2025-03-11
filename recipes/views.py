from django.shortcuts import render                           # imported by default
from .models import Recipe                                    # to access the Recipe model
from django.views.generic import ListView, DetailView         # to display lists and details
from django.contrib.auth.mixins import LoginRequiredMixin     # to protect class-based view
from django.contrib.auth.decorators import login_required     # to protect function-based view
from django.contrib import messages                           # import Django messages framework
from .forms import RecipeSearchForm                           # import RecipeSearchForm class
import pandas as pd                                           # import pandas. refer to it as 'pd'
from .utils import get_chart                                  # to call the get_chart() function

# Create your views here.

class RecipeListView(LoginRequiredMixin, ListView):           # class-based "protected" view
  model = Recipe                                              # specify model
  template_name = 'recipes/recipes_home.html'                 # specify template

class RecipeDetailView(LoginRequiredMixin, DetailView):       # class-based "protected" view
  model = Recipe                                              # specify model
  template_name = 'recipes/recipe_details.html'               # specify template

# This function takes the request coming from the web application and, 
# returns the template available at recipes/home.html as a response
def home(request):
  return render(request, 'recipes/recipes_home.html')

@login_required # protected
def recipe_list(request):
  form = RecipeSearchForm(request.GET or None) # Create an instance of RecipeSearchForm that was defined in recipes/forms.py. Allow GET requests for filtering
  qs_recipes = Recipe.objects.all() # Retrieve all recipes from the database (a QuerySet)
  recipes_df = None # Initialize pandas DataFrame as None
  chart = None # Initialize chart variable as None
  chart_error_msg = None # Initialize an error message variable

  # Get search input from the form
  recipe_name = request.GET.get('recipe_name', '').strip() # Get recipe name input from the search form
  ingredient = request.GET.get('ingredient', '').strip() # Get ingredient input from the search form
  difficulty = request.GET.get('difficulty', '') # Get difficulty level selection from the search form
  chart_type = request.GET.get('chart_type', '') # Get chart type selection from the search form

  # Apply filters based on user input (only if any filter is present)
  if recipe_name or ingredient or difficulty:
    if recipe_name:
      qs_recipes = qs_recipes.filter(name__icontains=recipe_name) # Partial match
    if ingredient:
      qs_recipes = qs_recipes.filter(ingredients__icontains=ingredient) # Partial match
    if difficulty:
      qs_recipes = qs_recipes.filter(difficulty=difficulty) # Exact match

  if qs_recipes.exists(): # Convert the QuerySet to a Pandas DataFrame (if there are matching recipes/results)
    recipes_df = pd.DataFrame(qs_recipes.values()) # Convert QuerySet to DataFrame
    recipes_df = recipes_df.to_html() # Convert DataFrame to HTML table

    if chart_type: # Generate chart if a chart type is selected
      chart = get_chart(chart_type, pd.DataFrame(qs_recipes.values()))
      if chart is None: # Check if get_chart() returned None
        chart_error_msg = 'Invalid chart type selected. Please choose a valid chart.'

  # Pass recipes, form, and chart to the template (recipes_list.html file)
  return render(request, 'recipes/recipes_list.html', {
def login_view(request):
  """ Handles user authentication using Django's built-in AuthenticationForm. """

  error_message = None
  form = AuthenticationForm()

  # Process form submission when the user clicks "Login" button
  if request.method == 'POST':
    # Populate form with submitted data
    form = AuthenticationForm(data = request.POST)

    if form.is_valid():
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password')
      # Use Django 'authenticate' function to authenticate user
      user = authenticate(username = username, password = password)
      
      if user is not None:
        # if user is authenticated, use pre-defined Django function to log in
        login(request, user)
        return redirect('recipes:recipe_list')
      else:
        error_message = 'Oops... something went wrong!'

  context = {
    'form': form,
    'error_message': error_message,
  }

  return render(request, 'recipes/auth/login.html', context)

def signup_view(request):
  """ Handles user signup, form validation, and automatic login after successful signup. """

  error_message = None
  success_message = None
  form = SignupForm()

  # Check if request is a form submission (POST request)
  if request.method == 'POST':
    
    # Populate form with submitted user data
    form = SignupForm(request.POST)
    
    if form.is_valid():
      # Save the new user to the database
      user = form.save()
      # Automatically log in the user after signup
      login(request, user)
      success_message = 'User has been successfully created!'

      # Clone public recipes from the superuser to the newly created user
      superuser = User.objects.get(username='evandanowitz') # Retrieve the superuser account
      public_recipes = Recipe.objects.filter(user=superuser) # Get all public recipes
      
      for recipe in public_recipes:
        # Create a copy of each public recipe for the new user
        Recipe.objects.create(
          user=user,
          name=recipe.name,
          cooking_time=recipe.cooking_time,
          ingredients=recipe.ingredients,
          difficulty=recipe.difficulty,
          description=recipe.description,
          pic=recipe.pic,
        )

      # Reset form after successful signup
      form = SignupForm()

    else:
      # Display detailed error messages for invalid form submission
      error_message = form.errors.as_ul()

  context = {
    'form': form,
    'error_message': error_message,
    'success_message': success_message,
  }

  return render(request, 'recipes/auth/signup.html', context)

