from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    path("create-pocket/", views.create_pocket, name="create_pocket"),
    path("transaction/<int:transaction_id>/", views.transaction_detail, name="transaction_detail"),
    path(
        "transaction/delete/<int:transaction_id>",
        views.delete_transaction,
        name="app_delete_transaction_page",
    ),
    path(
        "pocket/<int:pocket_id>/transactions/",
        views.pocket_transactions,
        name="pocket_transactions",
    ),
    path(
        "pocket/<int:pocket_id>/transactions/create/",
        views.create_transaction,
        name="create_transaction",
    ),
]
