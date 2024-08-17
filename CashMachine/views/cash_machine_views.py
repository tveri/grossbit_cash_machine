import pdfkit, uuid, qrcode, base64
import qrcode.image.pil
from io import BytesIO, StringIO
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.utils.timezone import localtime
from django.http import FileResponse, HttpResponse

from .. import settings
from ..serializers import CheckListSerializer
from ..models import Item


class CashMachineAPIView(APIView):
    @staticmethod
    def post(request: Request):
        serializer = CheckListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        products = []
        for product_id in set(serializer.validated_data.get("items")):
            product = Item.objects.get(id=product_id)
            count = serializer.validated_data.get("items").count(product_id)
            products.append(
                {
                    "title": product.title,
                    "count": count,
                    "price": product.price * count,
                }
            )

        context = {
            "time": localtime().strftime("%d.%m.%Y %H:%M"),
            "products": products,
            "cost": sum([product["price"] for product in products]),
        }

        filename = f"{uuid.uuid4()}.pdf"
        checklist_string = render_to_string(
            "checklist_template/checklist_template.html", context=context
        )
        config = pdfkit.configuration(
            wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
        )
        pdfkit.from_string(
            checklist_string,
            settings.MEDIA_ROOT / filename,
            configuration=config,
            options={
                "page-size": "A5",
            },
        )

        qr = qrcode.make(f"http://{settings.HOST}/media/{filename}")
        response = HttpResponse(content_type="image/jpeg")
        qr.save(response, format="jpeg")
        return response
