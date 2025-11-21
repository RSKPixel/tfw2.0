from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def user_profile(request):
    # Dummy implementation for user profile
    user_profile = {
        "username": "testuser",
        "email": "testuser@example.com",
    }
    return Response(user_profile)


@api_view(["POST"])
def user_login(request):

    # Dummy implementation for user login
    username = request.data.get("username")
    password = request.data.get("password")
    if username == "testuser" and password == "password123":
        return Response({"status": "success", "message": "Login successful."})
    else:
        return Response(
            {"status": "error", "message": "Invalid credentials."}, status=401
        )
