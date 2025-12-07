from rest_framework.decorators import api_view
from rest_framework.response import Response
from data.kite_framework import kite_connect


@api_view(["POST"])
def profile(request):
    kiteapi, kite_response = kite_connect()
    if Response["status"] == "error":
        return Response(kite_response)

    profile = kiteapi.profile()
    return Response(
        {
            "status": "success",
            "message": "Profile fetched successfully.",
            "data": profile,
        },
    )


@api_view(["POST"])
def fetch_positions(request):
    kiteapi, kite_response = kite_connect()
    if Response["status"] == "error":
        return Response(kite_response)

    positions = kiteapi.positions()
    return Response(
        {
            "status": "success",
            "message": "Positions fetched successfully.",
            "data": positions,
        },
    )
