"""
URL configuration for tripexpensetracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from tripexpensetrackerapi.views import CategoryView, ExpenseCategoryView, ExpenseView, TripView, UserView, check_user, register_user

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'users', UserView, 'user')
router.register(r'trips', TripView, 'trip')
router.register(r'expenses', ExpenseView, 'expense')
router.register(r'expensecategories', ExpenseCategoryView, 'expensecategory')
router.register(r'categories', CategoryView, 'category')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    # Authentication-related paths
    path('checkuser', check_user, name='check-user'),
    path('register', register_user, name='register-user'),
    path('trips/<int:pk>/add_expense', TripView.as_view({'post': 'add_trip_expense'}), name='trip-add-expense'),
    path('trips/<int:pk>/remove_trip_expense/<int:expense_id>', TripView.as_view({'delete': 'remove_trip_expense'}), name='trip-remove-expense'),
    path('expenses/<int:pk>/remove_expense_category/<int:expense_category>', ExpenseView.as_view({'delete': 'remove_expense_category'}), name='expense-remove-expense-category')

]
