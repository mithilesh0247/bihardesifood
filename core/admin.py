from .models import Category, Product
from django.contrib import admin
from .models import Category, Product
from .models import Order
from django.contrib import admin
from .models import Order
from django.core.mail import send_mail
from django.conf import settings
from .utils import send_whatsapp_message, send_html_email


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'offer_price', 'available', 'category', 'stock']
    list_filter = ['available', 'category']
    search_fields = ['name', 'description']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'phone', 'email')
    list_editable = ('status',)
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        previous = Order.objects.filter(pk=obj.pk).first()
        super().save_model(request, obj, form, change)

        # Check if status changed
        if change and previous and previous.status != obj.status:
            print(f"🔔 Order {obj.id} status changed from {previous.status} to {obj.status}")

            # Prepare email content (HTML + text fallback)
            subject = f"Your Order #{obj.id} is {obj.status}"
            html_content = f"""
            <h2 style="color:#8B0000;">Bihar Desi Foods</h2>
            <div style="font-family: Arial, sans-serif; max-width:600px; margin:auto; padding:20px; border:1px solid #ddd; border-radius:10px;">
    <div style="text-align:center; margin-bottom:20px;">
        <img src="https://i.postimg.cc/MKvpgbTT/bihar-desi-food.png" alt="Bihar Desi Foods" width="150" style="border-radius:10px;">
    </div>
            <p>Hi {obj.customer_name},</p>
            <p>Your order <b>#{obj.id}</b> for <b>{obj.product.name}</b> is now <b>{obj.status}</b>.</p>
            <p>Thank you for shopping with us! 🎉</p>
            <p style="font-size:12px;">https://bihardesifood.com</p>
            """
            plain_message = f"Hi {obj.customer_name}, your order #{obj.id} for {obj.product.name} is now {obj.status}. 🎉 Thank you for shopping with Bihar Desi Foods!"

            # Send email
            if obj.email:
                send_html_email(subject, html_content, [obj.email])

            # Prepare WhatsApp + SMS message
            customer_message = f"""
Hi {obj.customer_name}, your order #{obj.id} for {obj.product.name} is now {obj.status}. 🎉
Thank you for shopping with Bihar Desi Foods!
"""

            # Send WhatsApp (with SMS fallback)
            if obj.phone:
                customer_whatsapp = f'whatsapp:+91{obj.phone}'
                send_whatsapp_message(customer_whatsapp, customer_message, fallback_sms=True)
