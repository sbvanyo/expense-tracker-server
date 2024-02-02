from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.decorators import action
from tripexpensetrackerapi.models import Trip, Expense, User, Category, ExpenseCategory
from tripexpensetrackerapi.views.expense_category_view import ExpenseCategorySerializer

class ExpenseView(ViewSet):
    """Expense view"""

    def retrieve(self, request, pk):
        """Handle GET requests for a single expense."""
        try:
            expense = Expense.objects.get(pk=pk)
            serializer = ExpenseSerializer(expense)
            return Response(serializer.data)
        except Expense.DoesNotExist:
            return Response({'message': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to get all expenses."""
        try:
            expenses = Expense.objects.all()
            serializer = ExpenseSerializer(expenses, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Handle POST operations, create a new expense."""
        try:
            user = User.objects.get(pk=request.data["user"])
            trip_id = request.data.get("trip")
            trip = Trip.objects.get(pk=trip_id) if trip_id else None

            expense = Expense.objects.create(
                user=user,
                name=request.data["name"],
                amount=request.data["amount"],
                description=request.data["description"],
                date=request.data["date"],
                trip=trip
            )

            # Checks if categories are provided in the request
            category_ids = request.data.get("categories")
            categories = []

            if category_ids:
                # Creates ExpenseCategory instances for the provided category IDs
                for category_id in category_ids:
                    category = Category.objects.get(pk=category_id)
                    expense_category = ExpenseCategory.objects.create(
                        category=category,
                        expense=expense,
                    )
                    categories.append(expense_category)

            # Assigns ExpenseCategory instances to the expense if provided
            expense.categories.set(categories)

            serializer = ExpenseSerializer(expense)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Trip.DoesNotExist:
            return Response({'message': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        """Handle PUT requests to update an expense."""
        try:
            expense = Expense.objects.get(pk=pk)
            user = User.objects.get(pk=request.data["user"])
            category_ids = request.data.get("categories", [])
            categories = Category.objects.filter(pk__in=category_ids)

            expense.user = user
            expense.name = request.data["name"]
            expense.amount = request.data["amount"]
            expense.description = request.data["description"]
            expense.date = request.data["date"]

            # Updates expense details
            expense.save()
            
            # Clears existing categories through ExpenseCategory only if new categories are provided
            if categories:
                ExpenseCategory.objects.filter(expense=expense).delete()

            # Adds new categories
            for category in categories:
                ExpenseCategory.objects.create(expense=expense, category=category)

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Expense.DoesNotExist:
            return Response({'message': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    def destroy(self, request, pk):
        try:
            expense = Expense.objects.get(pk=pk)

            # Fetch all associated ExpenseCategory instances
            expense_categories = ExpenseCategory.objects.filter(expense=expense)

            # Delete each ExpenseCategory
            for expense_category in expense_categories:
                expense_category.delete()

            # Now delete the expense
            expense.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Expense.DoesNotExist:
            return Response({'message': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # ADD/REMOVE expense categories

    @action(methods=['post'], detail=True)
    def add_expense_category(self, request, pk):
        """Post request for a user to add a category to an expense"""
        try:
            category = Category.objects.get(pk=request.data["category"])
            expense = Expense.objects.get(pk=pk)
            expense_category = ExpenseCategory.objects.create(
                category=category,
                expense=expense,
            )
            return Response({'message': 'Category added to expense'}, status=status.HTTP_201_CREATED)
        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(methods=['delete'], detail=True)
    def remove_expense_category(self, request, pk, expense_category):
        """Delete request for a user to remove a category from an expense"""
        try:
            expense_category = ExpenseCategory.objects.get(pk=expense_category, expense__pk=pk)
            expense_category.delete()

            return Response({"message": "Expense category removed"}, status=status.HTTP_204_NO_CONTENT)
        except ExpenseCategory.DoesNotExist:
            return Response({"error": "Expense category not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExpenseSerializer(serializers.ModelSerializer):
    """JSON serializer for expenses."""
    categories = ExpenseCategorySerializer(many=True, read_only=True, required=False)
    
    class Meta:
        model = Expense
        fields = ('id', 'name', 'user', 'amount', 'description', 'date', 'categories')
        depth = 1
