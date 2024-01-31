from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from tripexpensetrackerapi.models import ExpenseCategory, Expense, Category
from tripexpensetrackerapi.views.expense_view import ExpenseSerializer
from tripexpensetrackerapi.views.category_view import CategorySerializer

class ExpenseCategoryView(ViewSet):
    """ExpenseCategory view"""

    def retrieve(self, request, pk):
        """Handle GET requests for a single expense category."""
        try:
            expense_category = ExpenseCategory.objects.get(pk=pk)
            serializer = ExpenseCategorySerializer(expense_category)
            return Response(serializer.data)
        except ExpenseCategory.DoesNotExist:
            return Response({'message': 'Expense category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to get all expense categories."""
        try:
            expense_categories = ExpenseCategory.objects.all()
            serializer = ExpenseCategorySerializer(expense_categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Handle POST operations, create a new expense category."""
        try:
            expense = Expense.objects.get(pk=request.data["expense"])
            category = Category.objects.get(pk=request.data["category"])

            expense_category = ExpenseCategory.objects.create(
                expense=expense,
                category=category,
            )
            serializer = ExpenseCategorySerializer(expense_category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Expense.DoesNotExist:
            return Response({'message': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        """Handle PUT requests to update an expense category."""
        return Response({'message': 'Not supported'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        """Handle DELETE requests to delete an expense category."""
        try:
            expense_category = ExpenseCategory.objects.get(pk=pk)
            expense_category.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except ExpenseCategory.DoesNotExist:
            return Response({'message': 'Expense category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExpenseCategorySerializer(serializers.ModelSerializer):
    """JSON serializer for expense categories."""
    expense = ExpenseSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = ExpenseCategory
        fields = ('id', 'expense', 'category')
        depth = 1
