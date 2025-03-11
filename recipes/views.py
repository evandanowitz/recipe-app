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

@login_required
def recipe_list(request):
  """ Display the list of recipes, apply search filters, and generate charts. """
  
  form = RecipeSearchForm(request.GET or None)
  
  # Retrieve and remove any stored message about a deleted recipe
  deleted_recipe_message = request.session.pop('deleted_recipe_message', None)

  # Determine which recipes to show: Superusers see all; regular users see only their own
  if request.user.is_superuser:
    qs_recipes = Recipe.objects.filter(Q(user=request.user) | Q(user__isnull=True))
  else:
    qs_recipes = Recipe.objects.filter(user=request.user)

  # If a non-superuser has no recipes, clone public recipes for them
  if not qs_recipes.exists() and not request.user.is_superuser:
    public_recipes = Recipe.objects.filter(user__isnull=True)
    
    for recipe in public_recipes:
      Recipe.objects.create(
        user=request.user,
        name=recipe.name,
        cooking_time=recipe.cooking_time,
        ingredients=recipe.ingredients,
        difficulty=recipe.difficulty,
        description=recipe.description,
        pic=recipe.pic,
      )

    # Fetch updated list of user-specific recipes
    qs_recipes = Recipe.objects.filter(user=request.user)

  # Get user's display name (use full name if available, otherwise username)
  display_name = request.user.get_full_name() if request.user.get_full_name() else request.user.username

  recipes_df = None
  chart = None
  chart_error_msg = None

  # Retrieve user search inputs
  recipe_name = request.GET.get('recipe_name', '').strip()
  ingredient = request.GET.get('ingredient', '').strip()
  difficulty = request.GET.get('difficulty', '')
  chart_type = request.GET.get('chart_type', '')

  # Apply filters if any search criteria are provided
  if recipe_name or ingredient or difficulty:
    if recipe_name:
      qs_recipes = qs_recipes.filter(name__icontains=recipe_name)
    if ingredient:
      qs_recipes = qs_recipes.filter(ingredients__icontains=ingredient)
    if difficulty:
      qs_recipes = qs_recipes.filter(difficulty=difficulty)

  no_results_message = 'No recipes match your search criteria.' if not qs_recipes.exists() else None

  # Convert QuerySet to DataFrame and convert DataFrame to HTML table (if results exist)
  if qs_recipes.exists():
    recipes_df = pd.DataFrame(qs_recipes.values())
    recipes_df = recipes_df.to_html()

    if chart_type:
      chart = get_chart(chart_type, pd.DataFrame(qs_recipes.values()))
      if chart is None:
        chart_error_msg = 'Invalid chart type selected. Please choose a valid chart.'

  return render(request, 'recipes/recipes_list.html', {
    'object_list': qs_recipes, # 'object_list' is default naming and is really just 'qs_recipes'
    'form': form,
    'recipes_df': recipes_df,
    'chart': chart,
    'chart_error_msg': chart_error_msg,
    'deleted_recipe_message': deleted_recipe_message,
    'no_results_message': no_results_message,
    'display_name': display_name
  })

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

def logout_view(request):
  """ Logs out the user and redirects to the logout success page. """
  
  # Logs out current user with pre-defined Django function
  logout(request)
  
  return redirect('recipes:logout_success')

def logout_success(request):
  """ Displays the logout success page with the timestamp of logout. """
  
  # Format logout time
  logout_time = localtime(now()).strftime('%m/%d/%Y @ %I:%M %p')

  return render(request, 'recipes/auth/logout_success.html', {'logout_time': logout_time})

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

def about_me_view(request):
  """ Renders the About Me page. """
  
  return render(request, 'recipes/about_me.html')

@login_required
def profile_view(request):
  """ Renders the user profile page with relevant account details and a button for account deletion. """
  
  # Retrieve user's name
  display_name = request.user.get_full_name()

  # If name is empty or blank, default to username
  if not display_name.strip():
    display_name = request.user.username
  
  # Retrieve name or set default message if not provided
  name = request.user.get_full_name()
  if not name.strip():
    name = 'Name not created at signup'

  # Retrieve email or set default message if not provided
  email = request.user.email
  if not email:
    email = 'Email not created at signup'

  context = {
    'username': request.user.username,
    'display_name': display_name,
    'name': name,
    'email': email
  }

  return render(request, 'recipes/profile.html', context)

