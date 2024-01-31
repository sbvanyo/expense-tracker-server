from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.decorators import action
from tripexpensetrackerapi.models import Expense, User, Category, ExpenseCategory
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
            category_ids = request.data.getlist("categories")
            categories = Category.objects.filter(pk__in=category_ids)

            expense = Expense.objects.create(
                user=user,
                amount=request.data["amount"],
                description=request.data["description"],
                date=request.data["date"],
            )
            
            expense.categories.set(categories)
            
            serializer = ExpenseSerializer(expense)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        """Handle PUT requests to update an expense."""
        try:
            expense = Expense.objects.get(pk=pk)
            user = User.objects.get(pk=request.data["user"])
            category_ids = request.data.getlist("categories")
            categories = Category.objects.filter(pk__in=category_ids)

            expense.user = user
            expense.amount = request.data["amount"]
            expense.description = request.data["description"]
            expense.date = request.data["date"]
            
            expense.categories.set(categories)
            
            expense.save()
            
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
        """Handle DELETE requests to delete an expense."""
        try:
            expense = Expense.objects.get(pk=pk)
            expense.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Expense.DoesNotExist:
            return Response({'message': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    # ADD/REMOVE EXPENSECATEGORY

    @action(methods=['post'], detail=True)
    def add_expense_category(self, request, pk):
        """Post request for a user to add a category to an expense"""

        category = Category.objects.get(pk=request.data["category"])
        expense = Expense.objects.get(pk=pk)
        expensecategory = ExpenseCategory.objects.create(
            category=category,
            expense=expense,
        )
        return Response({'message': 'Category added to expense'}, status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=True)
    def remove_expense_category(self, request, pk):
        """Delete request for a user to remove a category from an expense"""

        expensecategory_id = request.data.get("expense_category")
        if not expensecategory_id:
            return Response({"error": "Order item ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            expense_category = ExpenseCategory.objects.get(pk=expensecategory_id, order__pk=pk)
            expense_category.delete()
            return Response({"message": "Expense category removed"}, status=status.HTTP_204_NO_CONTENT)
        except ExpenseCategory.DoesNotExist:
            return Response({"error": "Expense category not found"}, status=status.HTTP_404_NOT_FOUND)

class ExpenseSerializer(serializers.ModelSerializer):
    """JSON serializer for expenses."""
    categories = ExpenseCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Expense
        fields = ('id', 'user', 'amount', 'description', 'date', 'categories')
        depth = 1
