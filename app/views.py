from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from .models import Pocket,  Transaction, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
import json


def logout_page(request):
    logout(request)
    return redirect('/login')

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, 'Account created successfully.')
            return redirect('/login')
    
    return render(request, 'register.html')

def login_page(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required(login_url='login')
def home(request):
    user_pockets = Pocket.objects.filter(user=request.user)
    return render(request, 'home.html', {'pockets': user_pockets})


@login_required(login_url='login')
def pocket_transactions(request, pocket_id):
    pocket = get_object_or_404(Pocket, id=pocket_id, user=request.user)
    transactions = Transaction.objects.filter(pocket=pocket).order_by('-create_date')
    categories = Category.objects.filter(user=request.user)
    return render(request, 'pocket_transactions.html', {
        'pocket': pocket, 
        'transactions': transactions,
        'categories':categories,
        })

@login_required(login_url='login')
def create_pocket(request):
    if request.method == "POST":
        name = request.POST.get('name')
        start_credit = request.POST.get('start_credit')
        if name and start_credit:
            Pocket.objects.create(user=request.user, name=name, start_credit=start_credit)
            messages.success(request, 'Pocket created successfully!')
        elif name :
            Pocket.objects.create(user=request.user, name=name)
            messages.success(request, 'Pocket created successfully!')
        else:
            messages.error(request, 'Please fill out all fields.')
        return redirect('/')

@login_required(login_url='login')
def delete_transaction(request,transaction_id):
    # get the transactions
    transaction = get_object_or_404(Transaction, id=transaction_id)
    pocket = get_object_or_404(Pocket,id=transaction.pocket.id)
    user = request.user
    pocket_user = pocket.user
    # check permission

    if user == pocket_user:
        messages.success(request, "Transaction deleted successfully!")
        pocket.start_credit = pocket.start_credit + transaction.amount 
        pocket.save()
        transaction.delete()
        return redirect('pocket_transactions', pocket_id=pocket.id)
    else:
        return HttpResponse('no permission')
    


@login_required
def create_transaction(request, pocket_id):
    pocket = get_object_or_404(Pocket, id=pocket_id, user=request.user)
    if request.method == "POST":
        title = request.POST["title"]
        amount = float(request.POST["amount"])
        raw_categories = request.POST.get("categories", "[]")  # JSON string payment_recurring
        payment_recurring = request.POST.get('payment_recurring') == "true"
        frequency = request.POST.get('frequency') if payment_recurring else None
        recurring_date = request.POST.get('recurring_date') if payment_recurring else None

        print('frequency' ,frequency)
        print('payment_recurring' ,payment_recurring)
        print('recurring_date' ,recurring_date)
        category_objs = []
        try:
            categories_list = json.loads(raw_categories)  # parse JSON
            
            for cat in categories_list:
                if "value" in cat:  # existing category with ID
                    try:
                        existing_cat = Category.objects.get(
                            id=int(cat["value"]), 
                            user=request.user
                        )
                        category_objs.append(existing_cat)
                    except (ValueError, Category.DoesNotExist):
                        pass
                elif "name" in cat:
                    # new category
                    new_cat, created = Category.objects.get_or_create(
                        name=cat["name"],
                        user=request.user
                    )
                    category_objs.append(new_cat)
        except:
            pass    
        # Create Transaction
        try:
            transaction = Transaction.objects.create(
                pocket=pocket,
                title=title,
                amount=amount,
                payment_recurring=payment_recurring,
                frequency=frequency,
                recurring_date=recurring_date,
            )
            # ManyToMany: link all categories
            if category_objs != None and len(category_objs)!=0:
                transaction.categories.set(category_objs)
            pocket.start_credit -= amount
            pocket.save()
        except Exception as e:
            print(e)
        # If needed, update pocket credit
        # pocket.start_credit -= amount
        # pocket.save()

        return redirect("pocket_transactions", pocket_id=pocket_id)

    return redirect("pocket_transactions", pocket_id=pocket_id)

# @login_required
# def create_transaction(request, pocket_id):
#     pocket = get_object_or_404(Pocket, id=pocket_id, user=request.user)
#     if request.method == "POST":
#         title = request.POST.get('title')
#         amount = float(request.POST.get('amount'))
#         categories_input = request.POST.get('categories')  # JSON string from Tagify
#         create_date = request.POST.get('create_date')
#         payment_recurring = request.POST.get('payment_recurring') == "on"
#         frequency = request.POST.get('frequency') if payment_recurring else None
#         recurring_date = request.POST.get('recurring_date') if payment_recurring else None

#         # Parse categories from JSON
#         categories = json.loads(categories_input)
#         print(categories)

#         category_objects = []
#         for category in categories:
#             if 'value' in category and category['value'].isdigit():
#                 # Existing category (value is numeric ID)
#                 cat = Category.objects.filter(id=category['value'], user=request.user).first()
#                 if cat:
#                     category_objects.append(cat)
#             elif 'name' in category:
#                 # New category (create it)
#                 cat, created = Category.objects.get_or_create(
#                     name=category['name'],
#                     user=request.user
#                 )
#                 category_objects.append(cat)

#         # Create the transaction
#         transaction = Transaction.objects.create(
#             pocket=pocket,
#             title=title,
#             amount=amount,
#             create_date=create_date,
#             payment_recurring=payment_recurring,
#             frequency=frequency,
#             recurring_date=recurring_date,
#         )
#         # Add categories to the transaction
#         transaction.categories.set(category_objects)

#         # Update the pocket's credit
#         pocket.start_credit -= amount
#         pocket.save()

#         messages.success(request, "Transaction created successfully!")
#         return redirect('pocket_transactions', pocket_id=pocket_id)
#     else:
#         return redirect('pocket_transactions', pocket_id=pocket_id)

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, pocket__user=request.user)
    categories = Category.objects.all()

    if request.method == "POST":
        # Fetch form data
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('new_category')
        create_date = request.POST.get('create_date')
        payment_recurring = request.POST.get('payment_recurring') == "on"
        frequency = request.POST.get('frequency') if payment_recurring else None
        recurring_date = request.POST.get('recurring_date') if payment_recurring else None

        # Handle category
        if new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name)
        elif category_id:
            category = Category.objects.filter(id=category_id).first()
        else:
            category = None

        # Update transaction
        transaction.title = title
        transaction.amount = amount
        transaction.category = category
        transaction.create_date = create_date
        transaction.payment_recurring = payment_recurring
        transaction.frequency = frequency
        transaction.recurring_date = recurring_date
        transaction.save()

        messages.success(request, "Transaction updated successfully!")
        return redirect('pocket_transactions', pocket_id=transaction.pocket.id)

    return render(request, 'transaction_detail.html', {
        'transaction': transaction,
        'categories': categories,
    })
