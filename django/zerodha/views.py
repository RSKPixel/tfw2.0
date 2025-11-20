from rest_framework.decorators import api_view
from rest_framework.response import Response
from data.kite import kite_connect


@api_view(["POST"])
def profile(request):
    kiteapi, kite_response = kite_connect()
    if Response["status"] == "error":
        return Response(kite_response)

    profile = kiteapi.profile()
    print("Zerodha Profile:", profile)
    return Response(
        {
            "status": "success",
            "message": "Profile fetched successfully.",
            "data": profile,
        },
    )
