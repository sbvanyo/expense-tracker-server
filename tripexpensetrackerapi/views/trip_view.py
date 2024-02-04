from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.decorators import action
from tripexpensetrackerapi.models import Trip, Expense, User
from tripexpensetrackerapi.views.expense_view import ExpenseSerializer
from tripexpensetrackerapi.views.user_view import UserSerializer

class TripView(ViewSet):
    """Trip view"""

    def retrieve(self, request, pk):
        """Handle GET requests for a single trip."""
        try:
            trip = Trip.objects.get(pk=pk)
            serializer = TripSerializer(trip)
            return Response(serializer.data)
        except Trip.DoesNotExist:
            return Response({'message': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request):
        """Handle GET requests to get all trips for a specific user."""
        try:
            # Gets user ID from the request
            user_id = request.query_params.get('userId', None)

            # Filters trips based on the user's ID
            trips = Trip.objects.filter(user__id=user_id)

            serializer = TripSerializer(trips, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Handle POST operations, create a new trip."""
        try:
            user = User.objects.get(pk=request.data["userId"])
            trip = Trip.objects.create(
                user=user,
                name=request.data["name"],
                date=request.data["date"],
                description=request.data["description"],
            )
            serializer = TripSerializer(trip)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        """Handle PUT requests to update a trip."""
        try:
            trip = Trip.objects.get(pk=pk)
            trip.name = request.data["name"]
            trip.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Trip.DoesNotExist:
            return Response({'message': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def destroy(self, request, pk):
        """Handle DELETE requests to delete a trip"""
        try:
            trip = Trip.objects.get(pk=pk)

            # Fetches all associated expenses for the trip
            expenses = Expense.objects.filter(trip=trip)

            # Deletes each expense (this will trigger the ExpenseCategoryView logic cascade)
            for expense in expenses:
                expense.delete()

            # Now deletes the trip
            trip.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Trip.DoesNotExist:
            return Response({'message': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # ADD/REMOVE trip expenses
    
    @action(methods=['post'], detail=True)
    def add_trip_expense(self, request, pk):
        """Post request for a user to add an expense to a trip."""
        try:
            expense = Expense.objects.get(pk=request.data["expense"])
            trip = Trip.objects.get(pk=pk)
            
            # Adds expense to the trip
            trip.expenses.add(expense)
            return Response({'message': 'Expense added to trip'}, status=status.HTTP_201_CREATED)
        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['delete'], detail=True)
    def remove_trip_expense(self, request, pk, expense_id):
        """Delete request for a user to remove an expense from a trip."""
        try:
            trip = Trip.objects.get(pk=pk)
            
            # Retrieves the Expense instance
            expense = Expense.objects.get(pk=expense_id)

            # Checks if the expense is associated with the trip before removing
            if expense not in trip.expenses.all():
                return Response({'error': 'Expense is not associated with the trip.'}, status=status.HTTP_404_NOT_FOUND)

            # Removes the expense from the trip
            trip.expenses.remove(expense)
            
            return Response({'message': 'Expense removed from trip'}, status=status.HTTP_204_NO_CONTENT)
        
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TripSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    expense_details = ExpenseSerializer(source='expenses', many=True, read_only=True)

    class Meta:
        model = Trip
        fields = ('id', 'name', 'date', 'description', 'user_details', 'expense_details')
        depth = 1
