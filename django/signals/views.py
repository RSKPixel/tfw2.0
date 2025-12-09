from rest_framework.decorators import api_view
from rest_framework.response import Response
from ut import kbd1, kebf

# Create your views here.
@api_view(["POST"])
def trading_models(request):

    trading_models = ["KBD1", "KEBF"]
    trading_models = {
        "KBD1": "Key Breakout - Dow Theory 1",
        "KEBF": "Key Exhaustion Butter Fly Pattern",
    }


    return Response({"status": "success", "message": "Available trading models fetched successfully.", "data": trading_models})

